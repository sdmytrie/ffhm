"""
EVENT
"""

import pymongo
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from api.models import Competition, Concurrent, Event, Gender


@permission_required("scoresheet.add_event")
def event_add(request, concurrent_id, competition_id):
    """add event"""
    collection = pymongo.MongoClient("mongo", 27017).exalto.concurrent

    ident = concurrent_id.split("-")
    ident = concurrent_id
    competition = Competition.objects.get(id=competition_id)
    current_season_year = competition.season.end_date.year

    ffhmfac_user = collection.find(
        {
            "$and": [
                {"concurrent.result.code_adherent": concurrent_id},
                {"concurrent.result.saison": current_season_year},
            ]
        }
    ).next()

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

    draw = len(competition.event_set.all()) + 1
    Event.objects.create(
        competition_id=competition.id,
        ffhmfacClub=ffhmfac_user["concurrent"]["result"]["club"]["code"],
        clubName=ffhmfac_user["concurrent"]["result"]["club"]["nom"],
        concurrent_id=concurrent.id,
        draw=draw,
    )

    return HttpResponse()


@permission_required(["scoresheet.change_team", "scoresheet.add_event"])
def event_add_team(request, concurrent_id, competition_id, team_id):
    """add event to team"""
    collection = pymongo.MongoClient("mongo", 27017).exalto.concurrent

    ident = concurrent_id.split("-")
    ident = concurrent_id
    competition = Competition.objects.get(id=competition_id)
    current_season_year = competition.season.end_date.year

    ffhmfac_user = collection.find(
        {
            "$and": [
                {"concurrent.result.code_adherent": concurrent_id},
                {"concurrent.result.saison": current_season_year},
            ]
        }
    ).next()

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

    competition = Competition.objects.get(id=competition_id)
    event = Event.objects.create(
        competition_id=competition.id,
        ffhmfacClub=ffhmfac_user["concurrent"]["result"]["club"]["code"],
        clubName=ffhmfac_user["concurrent"]["result"]["club"]["nom"],
        concurrent_id=concurrent.id,
        team_id=team_id,
    )
    competition.countevents = competition.countevents + 1

    event.team.name = concurrent.clubName
    event.team.save()

    competition.save()

    return render(request, "scoresheet/team/team_competition_view.html", locals())


@permission_required("scoresheet.change_event")
def event_change_draw(request, value, event_id):
    """change event draw"""

    event = Event.objects.get(id=event_id)
    event.draw = value
    event.save()

    return HttpResponse()


@permission_required("scoresheet.change_event")
def event_change_weight(request, value, id_event):
    """change event weight"""

    event = Event.objects.get(id=id_event)
    event.weight = value
    event.save()

    return HttpResponse()


@permission_required("scoresheet.delete_event")
def event_delete(request, event_id):
    """delete event"""

    event = Event.objects.get(id=event_id)
    event.competition.countevents = event.competition.countevents - 1
    event.competition.save()
    event.delete()

    if event.competition.isteam:
        return redirect("scoresheet:team_competition_view", str(event.competition.id))
    return redirect("scoresheet:competition_view", str(event.competition.id))
