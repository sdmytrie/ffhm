"""
LEADER
"""

import re

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import redirect, render
import pymongo

from api.models import Competition, Concurrent, Event, Gender, Leader, Leadertype


@permission_required("scoresheet.change_competition")
def leader_add(request, concurrent_id, competition_id, leadertype_id):
    """add leader"""
    collection = pymongo.MongoClient("mongo", 27017).exalto.concurrent

    ident = concurrent_id
    competition = Competition.objects.get(id=competition_id)
    ffhmfac_user = collection.find(
        {"concurrent.result.code_adherent": concurrent_id}
    ).next()
    ffhmfac_licence = ffhmfac_user["concurrent"]["result"]["code_adherent"]

    try:
        concurrent = Concurrent.objects.get(ffhmfacUser=ident)
    except Concurrent.DoesNotExist:
        gender_id = 2
        if ffhmfac_user["concurrent"]["result"]["sexe"] == "F":
            gender_id = 3
        birth = ffhmfac_user["concurrent"]["result"]["date_de_naissance"].split("/")
        date_of_birth = f"{birth[2]}-{birth[1]}-{birth[0]}"
        concurrent = Concurrent(
            ffhmfacUser=ident,
            licence=ffhmfac_user["concurrent"]["result"]["code_adherent"],
            country=ffhmfac_user["concurrent"]["result"]["nationalite"],
            date_of_birth=date_of_birth,
            gender_id=gender_id,
        )
        concurrent.save()

    concurrent.firstname = ffhmfac_user["concurrent"]["result"]["prenom"].capitalize()
    concurrent.lastname = ffhmfac_user["concurrent"]["result"]["nom"].upper()
    concurrent.clubName = ffhmfac_user["concurrent"]["result"]["club"]["nom"]
    concurrent.ffhmfacClub = ffhmfac_user["concurrent"]["result"]["club"]["code"]
    concurrent.save()

    try:
        leader = Leader.objects.get(
            competition_id=competition_id, leadertype_id=leadertype_id
        )
        leader.concurrent_id = concurrent.id
        leader.save()
    except Leader.DoesNotExist:
        leader = Leader.objects.create(
            competition_id=competition_id,
            concurrent_id=concurrent.id,
            leadertype_id=leadertype_id,
        )

    template = "scoresheet/competition/competition_view.html"
    if competition.isteam:
        template = "scoresheet/team/team_competition_view.html"

    return render(request, template, locals())


@login_required
def leader_get(request, licence, current_competition, current_leadertype_id):
    """get Leader"""
    collection = pymongo.MongoClient("mongo", 27017).exalto.concurrent

    competition = Competition.objects.get(id=current_competition)
    event_list = competition.event_set.all()
    leader_list = competition.leader_set.all()
    licence_list = []
    for event in event_list:
        licence_list.append(event.concurrent.licence)

    for leader in leader_list:
        licence_list.append(leader.concurrent.licence)

    concurrent_list = []
    pipeline = [
        {"$match": {"concurrent.result.saison": competition.season.end_date.year}},
        {
            "$match": {
                "$or": [
                    {
                        "concurrent.result.code_adherent": re.compile(
                            licence, re.IGNORECASE
                        )
                    },
                    {"concurrent.result.nom": re.compile(licence, re.IGNORECASE)},
                ]
            }
        },
    ]
    if (
        int(current_leadertype_id) < 4
        or (int(current_leadertype_id) >= 9 and int(current_leadertype_id) <= 11)
        or int(current_leadertype_id) == 6
        or int(current_leadertype_id) == 5
    ):
        pipeline = [
            {"$match": {"concurrent.result.licence.type.code": "A"}},
            {"$match": {"concurrent.result.saison": competition.season.end_date.year}},
            {
                "$match": {
                    "$or": [
                        {
                            "concurrent.result.code_adherent": re.compile(
                                licence, re.IGNORECASE
                            )
                        },
                        {"concurrent.result.nom": re.compile(licence, re.IGNORECASE)},
                    ]
                }
            },
        ]
    data = '<django-objects version="1.0">'
    concurrent_list_buffer = list(collection.aggregate(pipeline))
    concurrent_list = list(
        {
            v["concurrent"]["result"]["code_adherent"]: v
            for v in concurrent_list_buffer
        }.values()
    )
    for excluded_event in Event.objects.filter(competition=competition).all():
        buffer = filter(
            lambda c: c["concurrent"]["result"]["code_adherent"]
            != str(excluded_event.concurrent.licence),
            concurrent_list,
        )
        concurrent_list = list(buffer)

    for excluded_concurrent in leader_list:
        buffer = filter(
            lambda c: c["concurrent"]["result"]["code_adherent"]
            != str(excluded_concurrent.concurrent.licence),
            concurrent_list,
        )
        concurrent_list = list(buffer)

    for concurrent in concurrent_list:
        # if int(current_leadertype_id) < 4:
        #     group_list = FfhmfacUserGroup.objects.using('ffhm_intranet').filter(
        #         user__id=concurrent.user.id
        #     )
        #     result = any(group.group.id == 11 for group in group_list)
        #     if not result:
        #         continue
        data = (
            data
            + '<object pk="'
            + str(concurrent["concurrent"]["result"]["code_adherent"])
            + '">'
        )
        data = (
            data
            + '<field name="number" type="CharField">'
            + concurrent["concurrent"]["result"]["code_adherent"]
            + "</field>"
        )
        data = (
            data
            + '<field name="first_name" type="CharField">'
            + concurrent["concurrent"]["result"]["nom"].upper()
            + "</field>"
        )
        data = (
            data
            + '<field name="last_name" type="CharField">'
            + concurrent["concurrent"]["result"]["prenom"].capitalize()
            + "</field>"
        )
        data = data + "</object>"
    data = data + "</django-objects>"

    return render(request, "scoresheet/concurrent/concurrent_json.html", locals())


@permission_required("scoresheet.change_competition")
def leader_view(request, competition_id, leadertype_id):
    """view leader"""

    competition = Competition.objects.get(id=competition_id)
    leadertype = Leadertype.objects.get(id=leadertype_id)

    try:
        leader = Leader.objects.get(
            competition_id=competition_id, leadertype_id=leadertype_id
        )
    except Leader.DoesNotExist:
        leader = Leader()

    return render(request, "scoresheet/leader/leader_view.html", locals())


@permission_required("scoresheet.delete_event")
def leader_delete(request, leader_id):
    """delete leader"""

    leader = Leader.objects.get(id=leader_id)
    competition = Competition.objects.get(id=leader.competition_id)
    if request.user.is_superuser or request.user.is_staff:
        leader.delete()

    if competition.isteam:
        return redirect("scoresheet:team_competition_view", competition.id)
    return redirect("scoresheet:competition_view", competition.id)
