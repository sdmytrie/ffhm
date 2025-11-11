import random

from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
import pymongo

from api.models import Competition, Concurrent, Season, Wallpaper


#
# INDEX
#
def index(request, season_id="0"):
    """Description"""
    collection = pymongo.MongoClient("mongo", 27017).exalto.concurrent
    title = "Accueil"
    page = "home"

    current_season = list(Season.objects.all().order_by("start_date").reverse())[0]
    if season_id == "0":
        season = current_season
    else:
        season = Season.objects.get(id=season_id)

    if request.user.is_authenticated:
        editorGroup = Group.objects.get(name="Editor")
        editorGroup.user_set.remove(request.user)

    season_url_value = reverse("scoresheet:index")
    season_list = Season.objects.all().order_by("start_date")

    competition_list = (
        Competition.objects.prefetch_related("gender", "user", "gender")
        .filter(season_id=season.id)
        .order_by("-start_date")
    )

    concurrent_count = Concurrent.objects.count()
    # collection.count_documents(
    #     {"concurrent.result.season": current_season.name.split(" ")[1].split("/")[0]}
    # )
    competition_valid_licence = collection.count_documents({})

    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        return render(request, "scoresheet/mobile_index.html", locals())

    return render(request, "scoresheet/index.html", locals())


def login(request):
    """Description"""
    return render(request, "scoresheet/login.html", locals())


def logout(request):
    """Description"""
    logout(request)
    return redirect(reverse("scoresheet:index"))
