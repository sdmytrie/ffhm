from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from . import views

app_name = 'api'

urlpatterns = [
    path(r'api-token-auth/', obtain_jwt_token),
    path(r'api-token-refresh/', refresh_jwt_token),
    path('competitions/', views.CompetitionList.as_view()),
    path('competitions/<int:pk>/', views.CompetitionDetail.as_view()),
]
