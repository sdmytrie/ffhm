"""
COMPETITION
"""

from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import permission_required, user_passes_test
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import redirect, render
from openpyxl import Workbook
from openpyxl.styles import Color, Font, PatternFill, colors
from openpyxl.writer.excel import save_virtual_workbook

from api.models import Attempt, Competition, Event, Leader, Leadertype, Region, Season
from scoresheet.forms import CompetitionForm

from .utils import *


@permission_required("scoresheet.change_competition")
def competition_close(request, competition_id):
    """close competition"""

    competition = Competition.objects.get(id=competition_id)
    competition.closed = True
    competition.save()

    if competition.isteam:
        return redirect("scoresheet:team_competition_view", str(competition.id))
    return redirect("scoresheet:competition_view", str(competition.id))


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def competition_open(request, competition_id):
    """open competition"""

    competition = Competition.objects.get(id=competition_id)
    competition.closed = False
    competition.save()

    if competition.isteam:
        return redirect("scoresheet:team_competition_view", str(competition.id))
    return redirect("scoresheet:competition_view", str(competition.id))


def competition_list_view(request, season_id="0", week_filter="0"):
    """view competition list"""

    title = "Compétitions"
    page = "competition_list_view"

    current_season = list(Season.objects.all().order_by("start_date").reverse())[0]
    if season_id == "0":
        season = current_season
    else:
        season = Season.objects.get(id=season_id)

    start = season.start_date
    end = season.end_date

    if season_id == "0" or season_id == str(current_season.id):
        today = date.today()
        if week_filter == "0":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif week_filter == "1":
            buffer_start = today - timedelta(days=today.weekday())
            start = buffer_start + timedelta(days=7)
            end = season.end_date
        elif week_filter == "2":
            buffer_start = today - timedelta(days=today.weekday())
            end = buffer_start - timedelta(days=8)
            start = season.start_date
        elif week_filter == "3":
            buffer_start = today - timedelta(days=today.weekday())
            start = buffer_start - timedelta(days=7)
            # start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)

    season_url_value = reverse("scoresheet:competition_list_view")

    season_list = Season.objects.all().order_by("start_date")
    seasonUrlValue = ""

    editor_group = Group.objects.get(name="Editor")
    if current_season.id == season.id:
        if request.user.is_authenticated:
            editor_group.user_set.add(request.user)
    else:
        if request.user.is_authenticated:
            editor_group.user_set.remove(request.user)

    if request.user.is_superuser:
        competition_list = (
            Competition.objects.prefetch_related("gender", "user", "gender")
            .filter(season_id=season.id, start_date__gte=start, start_date__lte=end)
            .order_by("-start_date")
        )
    elif request.user.is_staff:
        competition_list = (
            Competition.objects.prefetch_related("gender", "user", "gender")
            .filter(
                season_id=season.id,
                user__profile__region=request.user.profile.region,
                start_date__gte=start,
                start_date__lte=end,
            )
            .order_by("-start_date")
        )
    else:
        competition_list = (
            Competition.objects.prefetch_related("gender", "user", "gender")
            .filter(
                user__profile__club=request.user.profile.club,
                start_date__gte=start,
                start_date__lte=end,
                season_id=season.id,
            )
            .order_by("-start_date")
        )

    concurrent_count = Concurrent.objects.count()
    season_id = int(season_id)

    return render(
        request, "scoresheet/competition/competition_list_view.html", locals()
    )


@permission_required("scoresheet.delete_competition")
def competition_delete(request, competition_id):
    """delete competition"""

    competition = Competition.objects.get(id=competition_id)
    if not competition.closed or request.user.is_superuser:
        competition.delete()

    return redirect("scoresheet:competition_list_view")


def competition_view(request, competition_id):
    """view competition"""

    title = "Compétitions"
    page = "competition_list_view"
    all_done = True
    event_list = []
    # best_arr = -1
    # best_epj = -1
    # best_total = -1
    # best_total_arr = -1
    # best_total_epj = -1

    leadertype_list = Leadertype.objects.all().order_by("view_order")
    leader_list = Leader.objects.filter(competition=competition_id)
    leader_dict = dict()
    for leadertype in leadertype_list:
        leader_dict[leadertype] = None

    for leader in leader_list:
        leader_dict[leader.leadertype] = leader

    competition = Competition.objects.get(id=competition_id)

    if competition.closed:
        event_list = sort_closed_event_list(competition)
    else:
        event_list = sorted(competition.event_set.all())
        if len(event_list) > 0:
            next_event = event_list[0]

        if len(event_list) > 1:
            nextnext_event = event_list[1]
        event_list.sort(key=lambda x: x.draw)

    editor_group = Group.objects.get(name="Editor")

    # for event in competition.event_set.all():
    #     if event.total > best_total and event.total > 0:
    #         best_total = event.total
    #     if event.totalSet[0] > best_total_arr and event.totalSet[0] > 0:
    #         best_total_arr = event.totalSet[0]
    #     if event.totalSet[1] > best_total_epj and event.totalSet[1] > 0:
    #         best_total_epj = event.totalSet[1]
    #     for attempt in event.attempt_set.all():
    #         if attempt.validate != 1:
    #             continue
    #         if attempt.name == "ARR":
    #             if attempt.value > best_arr and attempt.value > 0:
    #                 best_arr = attempt.value
    #         else:
    #             if attempt.value > best_epj and attempt.value > 0:
    #                 best_epj = attempt.value

    if request.user.is_authenticated:
        editor_group.user_set.remove(request.user)
        if (
            request.user.profile.club == competition.user.profile.club
            and competition.closed is False
        ):
            editor_group.user_set.add(request.user)
        if (
            request.user.is_staff
            and competition.user.profile.region == request.user.profile.region
        ):
            editor_group.user_set.add(request.user)
    if competition.closed:
        if request.user_agent.is_mobile or request.user_agent.is_tablet:
            return render(
                request,
                "scoresheet/competition/mobile_competition_closed_view.html",
                locals(),
            )
        return render(
            request, "scoresheet/competition/competition_closed_view.html", locals()
        )
    else:
        return render(request, "scoresheet/competition/competition_view.html", locals())


@permission_required("scoresheet.add_competition")
def competition_add(request, season_id):
    """add competition"""

    title = "Compétitions"
    page = "competition_list_view"
    season = Season.objects.get(id=season_id)

    if request.method == "POST":
        form = CompetitionForm(request.POST)
        if form.is_valid():
            season = Season.objects.get(id=season_id)
            instance = form.save(commit=False)
            instance.season = season
            instance.user = request.user
            instance.place = instance.place.capitalize()
            if instance.user.profile.region is not None:
                region = Region.objects.get(name=instance.user.profile.region)
                instance.name = (
                    region.short
                    + " - "
                    + instance.kind.name
                    + " - "
                    + instance.place
                    + " - "
                    + instance.name
                )
            instance.save()
        return redirect("scoresheet:competition_list_view")
    else:
        form = CompetitionForm()

    return render(request, "scoresheet/competition/competition_add.html", locals())


@permission_required("scoresheet.change_competition")
def competition_edit(request, competition_id):
    """edit competition"""

    title = "Compétitions"
    competition = Competition.objects.get(id=competition_id)
    isteam = competition.isteam

    if request.method == "POST":
        form = CompetitionForm(request.POST, instance=competition)
        print(form.is_valid())
        if form.is_valid():
            instance = form.save(commit=False)
            instance.isteam = isteam
            instance.save()
        return redirect("scoresheet:competition_list_view")
    else:
        form = CompetitionForm(instance=competition)

    return render(request, "scoresheet/competition/competition_edit.html", locals())


def competitionXls(request, id_competition):
    """export to excel format"""

    event_list = []
    competition = Competition.objects.get(id=id_competition)
    event_list = sort_closed_event_list(competition)
    workbook = excelize(event_list, competition.name)

    response = HttpResponse(
        content=save_virtual_workbook(workbook),
        content_type="application/ms-excel",
    )
    # workbook.save(response)
    response["Content-Disposition"] = "attachment; filename=competition.xlsx"

    return response
