from django.contrib.auth.models import Group, User
from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from rest_framework import (authentication, generics, permissions, status,
                            viewsets)
# from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .models import Competition, Profile
from .permissions import IsCompetitionOwner
from .serializers import CompetitionSerializer


class CompetitionList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CompetitionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        current_profile = Profile.objects.get(user_id=user.id)

        if user.is_superuser:
            return Competition.objects.all().order_by('-start_date')
        elif user.is_staff:
            profil_from_region_list = Profile.objects.filter(region=current_profile.region)
            user_from_region_list = []
            for profile in profil_from_region_list:
                user_from_region_list.append(profile.user_id)
            return Competition.objects.filter(user_id__in=user_from_region_list).order_by('-start_date')
        else:
            profil_from_club_list = Profile.objects.filter(club=current_profile.club)
            user_from_club_list = []
            for profile in profil_from_club_list:
                user_from_club_list.append(profile.user_id)
            return Competition.objects.filter(user_id__in=user_from_club_list).order_by('-start_date')

class CompetitionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCompetitionOwner]
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
