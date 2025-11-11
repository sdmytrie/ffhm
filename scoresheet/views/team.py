"""
TEAM
"""

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from api.models import Competition, Team, Leadertype, Leader, Event

from .utils import sort_closed_event_list, iwf, provisional_iwf


@permission_required("scoresheet.add_team")
def team_add(request, name, competition_id):
    """add team to competition"""

    team = Team.objects.create(name=name, competition_id=competition_id)

    return redirect("scoresheet:team_competition_view", str(competition_id))


@permission_required("scoresheet.change_team")
def team_change_draw(request, value, team_id):
    """change team draw"""

    team = Team.objects.get(id=team_id)
    team.draw = value
    team.save()

    return HttpResponse()


@permission_required("scoresheet.change_team")
def team_change_name(request, value, team_id):
    """change name of team"""

    team = Team.objects.get(id=team_id)
    team.name = value
    team.save()

    return HttpResponse()


@permission_required("scoresheet.delete_team")
def team_delete(request, team_id):
    """delete team"""

    team = Team.objects.get(id=team_id)
    competition = team.competition
    team.delete()

    return redirect("scoresheet:team_competition_view", str(competition.id))


def team_competition_view(request, competition_id):
    """view team competition"""

    page = "competition_list_view"
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

    event_list = []

    competition = Competition.objects.get(id=competition_id)

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

    if not competition.closed:
        event_list = sorted(competition.event_set.all())
        if len(event_list) > 0:
            next_event = event_list[0]

        if len(event_list) > 1:
            nextnext_event = event_list[1]

    team_list = []
    team_list = list(
        Team.objects.filter(competition_id=competition.id).order_by("draw")
    )

    for team in team_list:
        team.event_list = event_list

    nb_team = len(team_list) + 1

    for team in team_list:
        team.prov_iwf = 0
        for event in team.event_set.all():
            team.prov_iwf += provisional_iwf(event)

    if competition.closed:
        team_list.sort(key=lambda x: -x.iwf)

        for team in team_list:
            team.event_sorted_list = list(Event.objects.filter(team_id=team.id))
            team.event_sorted_list.sort(
                key=lambda e: (
                    e.agecategory_id,
                    e.weightcategory_id,
                    -e.total,
                    e.totalSet[1],
                )
            )

        return render(
            request, "scoresheet/team/team_competition_closed_view.html", locals()
        )
    return render(request, "scoresheet/team/team_competition_view.html", locals())


# def team_competition_closed_view(request, competition_id):
#     """ view closed team competition """

#     leadertypeList = Leadertype.objects.all()
#     leaderList = Leader.objects.filter(competition=competition_id)
#     eventList = []
#     # orderedEventList = Event.objects.all().order_by('id')

#     competition = Competition.objects.get(id=competition_id)

#     # eventList = sortEventList(competition.event_set.all())

#     # if competition.closed:
#     #     # eventList = sortClosedEventList(competition)
#     #     eventList = sortEventTeamList(competition.event_set.all())
#     # else :
#         # eventList = sortEventL
#     eventList = sort_closed_event_list(competition.event_set.all())

#     # if len(eventList) > 0:
#     #     nextEvent = eventList[0]

#     teamList = []

#     for event in eventList:
#         if event.team in teamList:
#             continue
#         teamList.append(event.team)

#     for team in competition.team_set.all():
#         if team in teamList:
#             continue
#         teamList.append(team)

#     teamList.sort(key=lambda x: x.created_at)
#     teamList.sort(key=lambda x: x.draw)

#     return render(request, 'scoresheet/team/competition/view.html', locals())
