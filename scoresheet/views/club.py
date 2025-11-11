from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.models import Concurrent, Competition, Event, Gender


@csrf_exempt
def club_get_by_name(request):
    """get club by name"""

    motif = request.POST.get("motif")
    club_list = (
        Concurrent.objects.filter(clubName__icontains=motif)
        .order_by("clubName")
        .values("clubName")
        .distinct()
    )

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
