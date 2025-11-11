"""
RANKING
"""

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.urls import reverse

from api.models import Concurrent, Event, Season
from scoresheet.forms import RankingForm
from scoresheet.views import utils


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def ranking(request, season_id="0"):
    """ranking"""

    page = "ranking"
    event_list = dict()
    event_list_buffer = dict()
    current_season = list(
        Season.objects.all().order_by("start_date").reverse())[0]
    if season_id == "0":
        season = current_season
    else:
        season = Season.objects.get(id=season_id)
    season_url_value = reverse("scoresheet:ranking")

    season_list = Season.objects.all().order_by("start_date")
    seasonUrlValue = ""

    clubs = "all"
    if request.user.is_superuser:
        ranking_name = "national"
    elif request.user.is_staff:
        ranking_name = request.user.profile.region
        clubs = utils.get_clubs_from_region(request.user.profile.region)

    if request.method == "POST":
        form = RankingForm(request.POST)
        if form.is_valid():
            gender = form.cleaned_data.get("gender")
            age = form.cleaned_data.get("age")
            limit = 100
            concurrent_list = []
            for event in Event.objects.filter(
                concurrent__country="FR",
                concurrent__gender=gender,
                competition__season__id=season.id,
                competition__closed=True
            ).order_by("-iwf"):
                if event.concurrent in concurrent_list:
                    continue
                concurrent_list.append(event.concurrent)

            # for concurrent in Concurrent.objects.filter(country='FR', gender_id=gender):
            for concurrent in concurrent_list:
                if age not in event_list_buffer:
                    event_list_buffer[age] = []

                if age == "Scratch":
                    limit = 100
                    if request.user.is_superuser:
                        event_list_buffer[age] = event_list_buffer[age] + list(
                            concurrent.event_set.filter(
                                agecategory__name__in=(
                                    "U15", "U17", "U20", "SENIOR"),
                                competition__season_id=season.id,
                                competition__closed=True
                            ).order_by("-iwf")[:1]
                        )
                    elif request.user.is_staff:
                        event_list_buffer[age] = event_list_buffer[age] + list(
                            concurrent.event_set.filter(
                                agecategory__name__in=(
                                    "U15", "U17", "U20", "SENIOR"),
                                competition__user__profile__region=request.user.profile.region,
                                competition__season_id=season.id,
                                competition__closed=True
                            ).order_by("-iwf")[:1]
                        )
                else:
                    if request.user.is_superuser:
                        event_list_buffer[age] = event_list_buffer[age] + list(
                            concurrent.event_set.filter(
                                agecategory__name=age, competition__season_id=season.id
                            ).order_by("-iwf")[:1]
                        )
                    elif request.user.is_staff:
                        event_list_buffer[age] = event_list_buffer[age] + list(
                            concurrent.event_set.filter(
                                agecategory__name=age,
                                competition__user__profile__region=request.user.profile.region,
                                competition__season_id=season.id,
                                competition__closed=True
                            ).order_by("-iwf")[:1]
                        )
                if len(event_list_buffer[age]) > limit:
                    break

                event_list[age] = sorted(
                    event_list_buffer[age], key=lambda event: -event.iwf
                )
    else:
        form = RankingForm()

    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        return render(
            request,
            "scoresheet/ranking/mobile_ranking.html",
            locals(),
        )
    return render(request, "scoresheet/ranking/ranking.html", locals())
