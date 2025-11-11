from django.urls import include, path

import scoresheet.views

app_name = "scoresheet"

urlpatterns = [
    path("", scoresheet.views.views.index, name="index"),
    path("accounts/", include("django.contrib.auth.urls")),
    path(
        "agecategory/view/",
        scoresheet.views.agecategory.agecategory_view,
        name="agecategory_view",
    ),
    path(
        "agecategory/view/<season_id>",
        scoresheet.views.agecategory.agecategory_view,
        name="agecategory_view",
    ),
    path(
        "attempt/change/<value>/<attempt_id>",
        scoresheet.views.attempt.attempt_change,
        name="attempt_change",
    ),
    path(
        "attempt/validate/<value>/<attempt_id>",
        scoresheet.views.attempt.attempt_validate,
        name="attempt_validate",
    ),
    path(
        "club/search",
        scoresheet.views.club.club_get_by_name,
        name="club_get_by_name",
    ),
    path(
        "league/search",
        scoresheet.views.league.league_get_by_name,
        name="club_get_by_name",
    ),
    path(
        "competition/add/<season_id>",
        scoresheet.views.competition.competition_add,
        name="competition_add",
    ),
    path(
        "competition/close/<competition_id>",
        scoresheet.views.competition.competition_close,
        name="competition_close",
    ),
    path(
        "competition/delete/<competition_id>",
        scoresheet.views.competition.competition_delete,
        name="competition_delete",
    ),
    path(
        "competition/edit/<competition_id>",
        scoresheet.views.competition.competition_edit,
        name="competition_edit",
    ),
    path(
        "competition/list/view/",
        scoresheet.views.competition.competition_list_view,
        name="competition_list_view",
    ),
    path(
        "competition/list/view/<season_id>",
        scoresheet.views.competition.competition_list_view,
        name="competition_list_view",
    ),
    path(
        "competition/list/view/<season_id>/<week_filter>",
        scoresheet.views.competition.competition_list_view,
        name="competition_list_view",
    ),
    path(
        "competition/open/<competition_id>",
        scoresheet.views.competition.competition_open,
        name="competition_open",
    ),
    path(
        "competition/view/<competition_id>",
        scoresheet.views.competition.competition_view,
        name="competition_view",
    ),
    path(
        "competitionXls/<id_competition>",
        scoresheet.views.competition.competitionXls,
        name="competitionXls",
    ),
    path(
        "concurrent/get/<licence>/<current_competition>/<gender_id>",
        scoresheet.views.concurrent.concurrent_get,
        name="concurrent_get",
    ),
    path(
        "concurrent/search",
        scoresheet.views.concurrent.concurrent_get_by_name,
        name="concurrent_get_by_name",
    ),
    path(
        "event/add/<concurrent_id>/<competition_id>",
        scoresheet.views.event.event_add,
        name="event_add",
    ),
    path(
        "event/add/team/<concurrent_id>/<competition_id>/<team_id>",
        scoresheet.views.event.event_add_team,
        name="event_add_team",
    ),
    path(
        "event/change/draw/<value>/<event_id>",
        scoresheet.views.event.event_change_draw,
        name="event_change_draw",
    ),
    path(
        "event/change/weight/<value>/<id_event>",
        scoresheet.views.event.event_change_weight,
        name="event_change_weight",
    ),
    path(
        "event/delete/<event_id>",
        scoresheet.views.event.event_delete,
        name="event_delete",
    ),
    path(
        "leader/add/<concurrent_id>/<competition_id>/<leadertype_id>",
        scoresheet.views.leader.leader_add,
        name="leader_add",
    ),
    path(
        "leader/get/<licence>/<current_competition>/<current_leadertype_id>",
        scoresheet.views.leader.leader_get,
        name="leader_get",
    ),
    path(
        "leader/view/<competition_id>/<leadertype_id>",
        scoresheet.views.leader.leader_view,
        name="leader_view",
    ),
    path(
        "leader/delete/<leader_id>",
        scoresheet.views.leader.leader_delete,
        name="leader_delete",
    ),
    path("listing/", scoresheet.views.listing.listing, name="listing"),
    path(
        "listing/leader/",
        scoresheet.views.listing.listing_leader,
        name="listing_leader",
    ),
    path(
        "listing/leader/<season_id>",
        scoresheet.views.listing.listing_leader,
        name="listing_leader",
    ),
    path("listing/view", scoresheet.views.listing.listing_view, name="listing_view"),
    path("listing/form", scoresheet.views.listing.listing_form, name="listing_form"),
    path("listing/<season_id>", scoresheet.views.listing.listing, name="listing"),
    path(
        "minimumweightcategory/change/value/<value>/<minimumweightcategory_id>",
        scoresheet.views.minimumweightcategory.minimumweightcategory_change_value,
        name="minimumweightcategory_change_value",
    ),
    path(
        "minimumweightcategory/view/<gender_id>/<master>/",
        scoresheet.views.minimumweightcategory.minimumweightcategory_view,
        name="minimumweightcategory_view",
    ),
    path(
        "minimumweightcategory/view/<gender_id>/<master>/<season_id>",
        scoresheet.views.minimumweightcategory.minimumweightcategory_view,
        name="minimumweightcategory_view",
    ),
    path("ranking/", scoresheet.views.ranking.ranking, name="ranking"),
    path("ranking/<season_id>", scoresheet.views.ranking.ranking, name="ranking"),
    path("record/", scoresheet.views.record.record, name="record"),
    path("record/<season_id>", scoresheet.views.record.record, name="record"),
    path("search/", scoresheet.views.search.search, name="search"),
    path("search/<season_id>", scoresheet.views.search.search, name="search"),
    path("search/<concurrent_id>/", scoresheet.views.search.search, name="search"),
    path("search/<concurrent_id>/<season_id>",
         scoresheet.views.search.search, name="search"),
    path(
        "search-by-club/<club_name>/<league_name>/",
        scoresheet.views.search.search_by_club,
        name="search_by_club",
    ),
    path(
        "search-by-club/<club_name>/<league_name>/<season_id>",
        scoresheet.views.search.search_by_club,
        name="search_by_club",
    ),
    path(
        "team/add/<name>/<competition_id>",
        scoresheet.views.team.team_add,
        name="team_add",
    ),
    path(
        "team/change/draw/<value>/<team_id>",
        scoresheet.views.team.team_change_draw,
        name="team_change_draw",
    ),
    path(
        "team/change/name/<value>/<team_id>",
        scoresheet.views.team.team_change_name,
        name="team_Change_name",
    ),
    path(
        "team/competition/view/<competition_id>",
        scoresheet.views.team.team_competition_view,
        name="team_competition_view",
    ),
    # path('team/competition/closed/view/<competition_id>', scoresheet.views.team.team_competition_closed_view, name="team_competition_closed_view"),
    path(
        "team/delete/<team_id>", scoresheet.views.team.team_delete, name="team_delete"
    ),
    path(
        "weightcategory/view/",
        scoresheet.views.weightcategory.weightcategory_view,
        name="weightcategory_view",
    ),
    path(
        "weightcategory/view/<season_id>",
        scoresheet.views.weightcategory.weightcategory_view,
        name="weightcategory_view",
    ),
    path("<season_id>", scoresheet.views.views.index, name="index"),
]
