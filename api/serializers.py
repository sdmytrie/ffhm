from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .models import (Attempt, Competition, Concurrent, Event, Gender, Season,
                     Team, Weightcategory)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']

class SeasonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Season
        fields = ['id',
                  'name']
                  
class GenderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gender
        fields = ['id',
                  'name',
                  'verbosename']

class TeamSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Team
        fields = ['id',
                  'name',
                  'draw']

class ConcurrentSerializer(serializers.ModelSerializer):
    gender = GenderSerializer()

    class Meta:
        model = Concurrent
        fields = ['id',
                  'ffhmfacUser',
                  'ffhmfacClub',
                  'clubName',
                  'licence',
                  'firstname',
                  'lastname',
                  'country',
                  'date_of_birth',
                  'gender']

class WeightcategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Weightcategory
        fields = ['id', 'weight']

class AttemptSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Attempt
        fields = ['id',
                  'name',
                  'rank',
                  'validate',
                  'value',
                  'distance']

class EventSerializer(serializers.ModelSerializer):
    concurrent = ConcurrentSerializer()
    weightcategory = WeightcategorySerializer()
    team = TeamSerializer()
    attempt_set = AttemptSerializer(many=True)

    class Meta:
        model = Event
        fields = ['id',
                  'ffhmfacClub',
                  'clubName',
                  'concurrent',
                  'team',
                  'draw',
                  'weight',
                  'weightcategory',
                  'agecategory',
                  'minimumweightcategory',
                  'total',
                  'iwf',
                  'attempt_set']

class CompetitionSerializer(serializers.ModelSerializer):
    event_set = EventSerializer(many=True)
    gender = GenderSerializer()
    season = SeasonSerializer()

    class Meta:
        model = Competition
        fields = ['id',
                  'name',
                  'isteam',
                  'isminime',
                  'place',
                  'address',
                  'troop',
                  'countevents',
                  'start_date',
                  'season',
                  'gender',
                  'user',
                  'closed',
                  'event_set']
