from operator import ne

from django.core.management.base import BaseCommand
from icecream import ic

from api.models import (
    Agecategory,
    Attempt,
    Concurrent,
    Event,
    Gender,
    Minimumweightcategory,
    Record,
    RecordStandard,
    Season,
    Weightcategory,
)
from scoresheet.management.commands.lib import weightcategory
from scoresheet.management.commands.lib.agecategory import FfhmAgecategory
from scoresheet.management.commands.lib.event import FfhmEvent
from scoresheet.management.commands.lib.record import FfhmRecord
from scoresheet.management.commands.lib.treatment_senior import TreatmentSenior
from scoresheet.management.commands.lib.treatment_u20 import TreatmentU20
from scoresheet.management.commands.lib.treatment_u17 import TreatmentU17
from scoresheet.management.commands.lib.treatment_u15 import TreatmentU15


class Command(BaseCommand):
    def handle(self, *args, **options):
        _current_season = list(Season.objects.all().order_by("-id"))[0]
        last_season = list(Season.objects.all().order_by("-id"))[1]

        minimumweightcategories = Minimumweightcategory.objects.filter(
            weightcategory__agecategory__season=_current_season, name="REG"
        )
        for mini in minimumweightcategories:
            mini.name = "PRO"
            mini.save()

        minimumweightcategories = Minimumweightcategory.objects.filter(
            weightcategory__agecategory__season=_current_season, name="IRG"
        )
        for mini in minimumweightcategories:
            mini.name = "LIG"
            mini.save()
