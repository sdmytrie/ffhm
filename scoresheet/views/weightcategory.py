import datetime

from django.contrib.auth.models import Group, Permission, User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from api.models import Agecategory, Season


def weightcategory_view(request, season_id="0"):
    title = 'Catégories de poids'
    page = 'weightcategory_view'

    if request.user.is_authenticated:
        editor_group = Group.objects.get(name="Editor")
        editor_group.user_set.remove(request.user)

    if season_id == "0":
        season = list(Season.objects.all().order_by('start_date').reverse())[0]
    else:
        season = Season.objects.get(id=season_id)
    season_url_value = reverse('scoresheet:weightcategory_view')

    season_list = Season.objects.all().order_by('start_date')
    seasonUrlValue = ''

    m_line = []
    i=0
    f_agecategory_list = Agecategory.objects.filter(season_id=season.id, gender_id=3).exclude(name='U10')
    m_agecategory_list = Agecategory.objects.filter(season_id=season.id, gender_id=2).exclude(name='U10')
    
    time = (-1)*datetime.datetime.now().year
    m_min_list = [30, 40, 50, 60, 70, 80, 90, 100, 110]
    f_min_list = [30, 40, 50, 60, 70, 80, 90]
    test = [" "]
    return render(request, 'scoresheet/weightcategory/weightcategory_view.html', locals())
