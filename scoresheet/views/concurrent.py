"""
CONCURRENT
"""

import re

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.models import Competition, Concurrent, Event, Gender
import pymongo


@login_required
def concurrent_get(request, licence, current_competition, gender_id):
    """get concurrent"""
    collection = pymongo.MongoClient("mongo", 27017).exalto.concurrent

    competition = Competition.objects.get(id=current_competition)

    event_list = Event.objects.filter(competition_id=competition.id)
    leader_list = competition.leader_set.all()
    gender = Gender.objects.get(id=gender_id)
    licence_list = []
    concurrent_list = []
    current_season_year = competition.season.end_date.year

    for event in event_list:
        licence_list.append(event.concurrent.licence)

    for leader in leader_list:
        licence_list.append(leader.concurrent.licence)
    if gender.value == 0:
        pipeline = [
            {
                "$match": {
                    "concurrent.result.saison": current_season_year,
                }
            },
            {
                "$match": {
                    "$or": [
                        {"concurrent.result.licence.type.code": "CA"},
                        {"concurrent.result.licence.type.code": "CJ"},
                    ]
                }
            },
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
    else:
        sexe = "M"
        if gender.value == 2:
            sexe = "F"
        pipeline = [
            {
                "$match": {
                    "concurrent.result.saison": current_season_year,
                }
            },
            {
                "$match": {
                    "$or": [
                        {"concurrent.result.licence.type.code": "CA"},
                        {"concurrent.result.licence.type.code": "CJ"},
                    ]
                }
            },
            {"$match": {"concurrent.result.sexe": sexe}},
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
    concurrent_list = list(collection.aggregate(pipeline))
    for excluded_concurrent in leader_list:
        buffer = filter(
            lambda c: c["concurrent"]["result"]["code_adherent"]
            != str(excluded_concurrent.concurrent.licence),
            concurrent_list,
        )
        concurrent_list = list(buffer)

    for excluded_event in Event.objects.filter(competition=competition).all():
        buffer = filter(
            lambda c: c["concurrent"]["result"]["code_adherent"]
            != str(excluded_event.concurrent.licence),
            concurrent_list,
        )
        concurrent_list = list(buffer)

    data = '<django-objects version="1.0">'
    for concurrent in concurrent_list:
        age = competition.season.end_date.year - int(
            concurrent["concurrent"]["result"]["date_de_naissance"].split("/")[2]
        )
        if competition.isminime:
            if age > 13:
                continue
        elif age < 14:
            continue
        if competition.ismasters:
            if age < 35:
                continue
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
            + concurrent["concurrent"]["result"]["prenom"].capitalize()
            + "</field>"
        )
        data = (
            data
            + '<field name="first_name" type="CharField">'
            + concurrent["concurrent"]["result"]["nom"].upper()
            + "</field>"
        )
        data = data + "</object>"
    data = data + "</django-objects>"

    return render(request, "scoresheet/concurrent/concurrent_json.html", locals())


def concurrent_get_by_name(request):
    """get concurrent by name"""

    motif = request.POST.get("motif")
    page = int(request.POST.get("page", "0"))
    count = concurrent_list = Concurrent.objects.filter(
        Q(lastname__icontains=motif)
        | Q(firstname__icontains=motif)
        | Q(licence__icontains=motif)
    ).count()
    concurrent_list = Concurrent.objects.filter(
        Q(lastname__icontains=motif)
        | Q(firstname__icontains=motif)
        | Q(licence__icontains=motif)
    ).order_by("lastname")[page * 10 : page * 10 + 10]
    context = {
        "concurrent_list": concurrent_list,
        "page": page,
        "motif": motif,
        "count": count,
        "total": (page + 1) * 10,
    }
    return render(request, "scoresheet/partials/concurrent_search_table.html", context)

    data = '<django-objects version="1.0">'
    for concurrent in concurrent_list:
        data = data + '<object pk="' + str(concurrent.id) + '">'
        data = (
            data
            + '<field name="licence" type="CharField">'
            + concurrent.licence
            + "</field>"
        )
        data = (
            data
            + '<field name="first_name" type="CharField">'
            + concurrent.firstname.capitalize()
            + "</field>"
        )
        data = (
            data
            + '<field name="first_name" type="CharField">'
            + concurrent.lastname.upper()
            + "</field>"
        )
        data = data + "</object>"
    data = data + "</django-objects>"

    return render(request, "scoresheet/concurrent/concurrent_json.html", locals())
