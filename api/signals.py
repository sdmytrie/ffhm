import os

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from icecream import ic

from PIL import Image
import pymongo

from .models import *


@receiver(pre_save, sender=Wallpaper)
def set_wallpaper_name(sender, instance, **kwargs):
    if sender == Wallpaper:
        instance.name = instance.wallpaper.name


@receiver(pre_delete, sender=Wallpaper)
def remove_wallpaper_file(sender, instance, **kwargs):
    if sender == Wallpaper:
        wallpaper = Wallpaper.objects.get(id=instance.id)
        wallpaper_path = os.path.join(
            f"/app/ffhm/static/scoresheet/img/wallpapers/{wallpaper.name}"
        )
        try:
            os.remove(wallpaper_path)
        except Exception as e:
            pass


@receiver(post_save, sender=Attempt)
def add_minimumweightcategory(sender, instance, **kwargs):
    if sender == Attempt:
        if (
            instance.event.agecategory.name != "U10"
            and instance.event.agecategory.name != "U13"
        ):
            arr_total = instance.event.totalSet[0]
            epj_total = instance.event.totalSet[1]
            # total = instance.event.total
            total = int(arr_total) + int(epj_total)
            instance.event.minimumweightcategory = None
            if arr_total > 0 and epj_total > 0:
                minimumweightcategoryList = list(
                    instance.event.weightcategory.minimumweightcategory_set.all().order_by(
                        "weight"
                    )
                )
                current = None
                for minimumweightcategory in minimumweightcategoryList:
                    if total < minimumweightcategory.weight:
                        instance.event.minimumweightcategory = current
                        # instance.event.save()
                        break
                    current = minimumweightcategory
                if (
                    not instance.event.minimumweightcategory
                    and instance.event.total >= minimumweightcategoryList[-1].weight
                ):
                    instance.event.minimumweightcategory = minimumweightcategoryList[-1]

            instance.event.save()


@receiver(pre_save, sender=Attempt)
def add_distance(sender, instance, **kwargs):
    if sender == Attempt and instance.rank > 1:
        attempt2 = Attempt.objects.get(
            event_id=instance.event_id, name=instance.name, rank=instance.rank - 1
        )
        instance.distance = int(attempt2.value) - int(instance.value)


@receiver(post_save, sender=Event)
def create_attempt(sender, instance, created, **kwargs):
    if created and sender == Event:
        Attempt.objects.create(name="ARR", rank=1, value=0, event_id=instance.id)
        Attempt.objects.create(name="ARR", rank=2, value=0, event_id=instance.id)
        Attempt.objects.create(name="ARR", rank=3, value=0, event_id=instance.id)
        Attempt.objects.create(name="EP-J", rank=1, value=0, event_id=instance.id)
        Attempt.objects.create(name="EP-J", rank=2, value=0, event_id=instance.id)
        Attempt.objects.create(name="EP-J", rank=3, value=0, event_id=instance.id)

        instance.competition.countevents = instance.competition.countevents + 1
        instance.competition.save()


@receiver(pre_save, sender=Event)
def add_categories(sender, instance, **kwargs):
    if sender == Event:
        # Add Agecategory
        instance.agecategory = None
        # age = int((instance.competition.season.end_date.year - instance.concurrent.date_of_birth.year).days / 365.25)
        age = (
            instance.competition.season.end_date.year
            - instance.concurrent.date_of_birth.year
        )

        if instance.competition.ismasters:
            agecategoryList = list(
                Agecategory.objects.filter(
                    season_id=instance.competition.season.id,
                    gender_id=instance.concurrent.gender_id,
                ).order_by("agemin")
            )
        else:
            agecategoryList = list(
                Agecategory.objects.filter(
                    season_id=instance.competition.season.id,
                    gender_id=instance.concurrent.gender_id,
                )
                .exclude(name__startswith="M")
                .exclude(name__startswith="W")
                .order_by("agemin")
            )

        current = agecategoryList[0]
        for agecategory in agecategoryList:
            if age <= current.agemax:
                instance.agecategory = current
                break
            current = agecategory

        if not instance.agecategory:
            instance.agecategory = agecategoryList[-1]

        # Add Weightcategory
        current_weightcategoryList = []
        instance.weightcategory = None
        if float(instance.weight) == 0.0 or instance.agecategory.name == "U10":
            instance.weightcategory = None
        else:
            weightcategoryList = list(
                Weightcategory.objects.filter(agecategory_id=instance.agecategory.id)
            )
            for weightcategory in weightcategoryList:
                if ">" in weightcategory.weight:
                    max_weightcategory = weightcategory
                    continue
                current_weightcategoryList.append(weightcategory)

            current_weightcategoryList.sort(key=lambda w: float(w.weight))
            current = weightcategoryList[0]

            for weightcategory in current_weightcategoryList:
                if float(instance.weight) <= float(current.weight):
                    instance.weightcategory = current
                    break
                current = weightcategory

            current_max_weightcategory = current_weightcategoryList[-1]
            if not instance.weightcategory:
                instance.weightcategory = current_max_weightcategory

            if float(instance.weight) > float(current_max_weightcategory.weight):
                instance.weightcategory = max_weightcategory


@receiver(post_save, sender=Season)
def create_categories(sender, instance, created, **kwargs):
    if created and sender == Season:
        preSeason = Season.objects.all().exclude(id=instance.id).latest("created_at")
        instance.preseason_id = preSeason.id
        instance.save()

        for agecategory in preSeason.agecategory_set.all():
            new_agecategory = Agecategory.objects.create(
                name=agecategory.name,
                surname=agecategory.surname,
                gender_id=agecategory.gender.id,
                agemin=agecategory.agemin,
                agemax=agecategory.agemax,
                season_id=instance.id,
            )
            for weightcategory in agecategory.weightcategory_set.all():
                new_weightcategory = Weightcategory.objects.create(
                    agecategory_id=new_agecategory.id, weight=weightcategory.weight
                )
                for (
                    minimumweightcategory
                ) in weightcategory.minimumweightcategory_set.all():
                    Minimumweightcategory.objects.create(
                        name=minimumweightcategory.name,
                        weight=minimumweightcategory.weight,
                        weightcategory_id=new_weightcategory.id,
                    )


@receiver(pre_delete, sender=Team)
def countevents(sender, instance, **kwargs):
    if sender == Team:
        countevents = instance.event_set.count()
        instance.competition.countevents = (
            instance.competition.countevents - countevents
        )
        instance.competition.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # profile = Profile.objects.get_or_create(user=instance)
    # if not hasattr(instance, 'profile'):
    #     Profile.objects.create(user=instance)
    collection = pymongo.MongoClient("mongo", 27017).exalto.concurrent
    if instance.profile.licence:
        try:
            user = next(
                collection.find(
                    {"concurrent.result.code_adherent": instance.profile.licence}
                ),
                None,
            )
        except:
            user = None

        if user is not None:
            instance.profile.club = user["concurrent"]["result"]["club"]["nom"]
            instance.profile.region = user["concurrent"]["result"]["club"]["region"][
                "nom"
            ]
    else:
        instance.profile.club = "Inconnu"
        # instance.profile.region = "Inconnu"
    instance.profile.save()


@receiver([post_save, post_delete], sender=Record)
def invalidate_record_cache(sender, instance, **kwargs):
    cache.delete_pattern("*record_list*")
