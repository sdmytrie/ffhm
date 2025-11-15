from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.models import Concurrent, Competition, Event, Gender


@csrf_exempt
def club_get_by_name(request):
    """get club by name"""

    motif = request.POST.get("motif")
    page = int(request.POST.get("page", "0"))
    count = (
        Concurrent.objects.filter(clubName__icontains=motif)
        .order_by("clubName")
        .values("clubName")
        .distinct()
        .count()
    )
    club_list = list(
        Concurrent.objects.filter(clubName__icontains=motif)
        .order_by("clubName")
        .values("clubName")
        .distinct()[page * 10 : page * 10 + 10]
    )
    context = {
        "club_list": club_list,
        "page": page,
        "motif": motif,
        "count": count,
        "total": (page + 1) * 10,
    }
    return render(request, "scoresheet/partials/club_search_table.html", context)

    data = '<django-objects version="1.0">'
    for club in list(club_list):
        data = data + '<object pk="' + str(club.get("clubName")) + '">'
        data = (
            data
            + '<field name="club" type="CharField">'
            + club.get("clubName")
            + "</field>"
        )
        data = data + "</object>"
    data = data + "</django-objects>"

    return render(request, "scoresheet/club/club_json.html", locals())
