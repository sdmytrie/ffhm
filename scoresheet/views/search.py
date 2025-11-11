"""
SEARCH
"""

from django.shortcuts import render
from django.contrib.auth.models import Group
from django.urls import reverse

from api.models import Concurrent, Event, Season

from scoresheet.views.utils import get_clubs_from_region


def search(request, concurrent_id="0", season_id="0"):
    """search"""

    page = "search"
    current_season = list(
        Season.objects.all().order_by("start_date").reverse())[0]
    if season_id == "0":
        season = current_season
    else:
        season = Season.objects.get(id=season_id)

    if request.user.is_authenticated:
        editorGroup = Group.objects.get(name="Editor")
        editorGroup.user_set.remove(request.user)

    season_url_value = reverse("scoresheet:search")
    if int(concurrent_id) > 0:
        season_url_value = reverse("scoresheet:search", kwargs={
            'concurrent_id': concurrent_id})

    season_list = Season.objects.all().order_by("start_date")

    # current_season = list(Season.objects.all().order_by('start_date').reverse())[0]
    id = int(concurrent_id)
    concurrent = None
    if id > 0:
        concurrent = Concurrent.objects.get(id=id)
        event_list = list(
            Event.objects.filter(competition__season__id=season.id).filter(concurrent_id=concurrent.id).order_by(
                "-competition__start_date"
            )
        )

    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        return render(request, "scoresheet/search/mobile_search.html", locals())

    return render(request, "scoresheet/search/search.html", locals())


def search_by_club(request, club_name, league_name, season_id="0"):
    page = "search"
    clubs = []

    current_season = list(
        Season.objects.all().order_by("start_date").reverse())[0]
    if season_id == "0":
        season = current_season
    else:
        season = Season.objects.get(id=season_id)

    if request.user.is_authenticated:
        editorGroup = Group.objects.get(name="Editor")
        editorGroup.user_set.remove(request.user)

    season_url_value = reverse(
        "scoresheet:search_by_club", kwargs={'club_name': club_name, 'league_name': league_name})
    season_list = Season.objects.all().order_by("start_date")
    if league_name == "0":
        club = club_name.replace("%20", " ")
        clubs.append(club)
    else:
        league = league_name.replace("%20", " ")
        clubs = get_clubs_from_region(league)

    if clubs:
        # concurrent = Concurrent.objects.get(id=id)
        event_list = list(
            Event.objects.prefetch_related("concurrent", "competition")
            .filter(competition__season__id=season.id)
            .filter(clubName__in=clubs)
            .order_by("-competition__start_date")
        )

    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        return render(request, "scoresheet/search/mobile_search.html", locals())

    return render(request, "scoresheet/search/search.html", locals())
