"""
    AGECATEGORY
"""
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.urls import reverse

from api.models import Agecategory, Season


def agecategory_view(request, season_id="0"):
    """ view agecategory """

    title = 'Catégories d\'âge'
    page = 'agecategory_view'

    if request.user.is_authenticated:
        editor_group = Group.objects.get(name="Editor")
        editor_group.user_set.remove(request.user)

    if season_id == "0":
        season = list(Season.objects.all().order_by('start_date').reverse())[0]
    else:
        season = Season.objects.get(id=season_id)
    season_url_value = reverse('scoresheet:agecategory_view')

    season_list = Season.objects.all().order_by('start_date')
    season_url_value = ''

    f_agecategory_list = Agecategory.objects.filter(
            season_id=season.id,
            gender_id=3
    )
    m_agecategory_list = Agecategory.objects.filter(
            season_id=season.id,
            gender_id=2
    )
    time = (-1)*season.end_date.year
    return render(
            request,
            'scoresheet/agecategory/agecategory_view.html',
            locals()
    )
