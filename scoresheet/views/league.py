from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.models import Profile, Competition, Event, Gender


@csrf_exempt
def league_get_by_name(request):
    """get club by name"""

    motif = request.POST.get("motif")
    league_list = (
        Profile.objects.filter(region__icontains=motif)
        .order_by("region")
        .values("region")
        .distinct()
    )

    data = '<django-objects version="1.0">'
    for league in list(league_list):
        data = data + '<object pk="' + str(league.get("region")) + '">'
        data = (
            data
            + '<field name="club" type="CharField">'
            + league.get("region")
            + "</field>"
        )
        data = data + "</object>"
    data = data + "</django-objects>"

    return render(request, "scoresheet/league/league_json.html", locals())
