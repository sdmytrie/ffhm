"""
    MINIMUMWEIGHTCATEGORY
"""
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import render

from api.models import *


def minimumweightcategory_view(request, gender_id, master, season_id="0"):
    """ view minimumweightcategory """

    title = 'Minima'
    page = 'minimumweightcategoryView'

    if request.user.is_authenticated:
        editor_group = Group.objects.get(name="Editor")
        editor_group.user_set.remove(request.user)

    if season_id == "0":
        season = list(Season.objects.all().order_by('start_date').reverse())[0]
    else:
        season = Season.objects.get(id=season_id)
    season_url_value = reverse('scoresheet:minimumweightcategory_view',
                                args=(gender_id, master))

    gender = Gender.objects.get(id=gender_id)

    season_list = Season.objects.all().order_by('start_date')

    if master == "0":
        agecategory_list = Agecategory.objects.filter(
            gender_id=gender_id, season_id=season_id
        ).exclude(name='U10').exclude(name='U13').exclude(name__startswith='M').exclude(name__startswith='W')
    else:
        agecategory_list = Agecategory.objects.filter(
            gender_id=gender_id, season_id=season_id
        ).exclude(name__startswith='U').exclude(name__startswith='SENIOR')
    return render(request, 'scoresheet/weightcategory/minimumweightcategory_view.html', locals())


@permission_required('scoresheet.change_minimumweightcategory')
def minimumweightcategory_change_value(request, value, minimumweightcategory_id):
    """ chnage minimumweigthcategory value """

    minimumweightcategory = Minimumweightcategory.objects.get(id=minimumweightcategory_id)

    minimumweightcategory.weight = value
    minimumweightcategory.save()

    return HttpResponse()
