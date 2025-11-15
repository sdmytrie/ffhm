from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.models import Profile, Competition, Event, Gender


@csrf_exempt
def league_get_by_name(request):
    """get league by name"""

    motif = request.POST.get("motif")
    page = int(request.POST.get("page", "0"))
    count = (
        Profile.objects.filter(region__icontains=motif)
        .order_by("region")
        .values("region")
        .distinct()
        .count()
    )
    league_list = (
        Profile.objects.filter(region__icontains=motif)
        .order_by("region")
        .values("region")
        .distinct()[page * 10 : page * 10 + 10]
    )
    context = {
        "league_list": league_list,
        "page": page,
        "motif": motif,
        "count": count,
        "total": (page + 1) * 10,
    }

    return render(request, "scoresheet/partials/league_search_table.html", context)
