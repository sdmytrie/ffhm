from rest_framework import permissions

from .models import Profile

class IsCompetitionOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        profile = Profile.objects.get(user_id=obj.user.id)
        region = profile.region
        club = profile.club


        if user.is_superuser:
            return True
        elif user.is_staff:
            return user.profile.region == region
        else:
            return user.profile.club == club and not obj.closed
