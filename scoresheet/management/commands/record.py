from operator import ne

from django.core.management.base import BaseCommand
from icecream import ic

from api.models import (
    Agecategory,
    Attempt,
    Concurrent,
    Event,
    Gender,
    Record,
    RecordStandard,
    Season,
    Weightcategory,
)
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

        _genders = ["male", "female"]
        _agecategories = ["SENIOR", "U20", "U17", "U15"]
        _kinds = ["ARR", "EP-J", "TOTAL"]
        #
        #
        # Recherche simple des records
        #
        ic("Simple record - start")
        for gender in _genders:
            for agecategory in _agecategories:
                _weightcategories = Weightcategory.objects.filter(
                    agecategory__name=agecategory,
                    agecategory__gender__name=gender,
                    agecategory__season=_current_season,
                ).order_by("weight")
                for kind in _kinds:
                    for weightcategory in _weightcategories:
                        _record = FfhmRecord(gender, agecategory, weightcategory, kind)
                        _current_record = _record.get_and_create_record()

                        _event = FfhmEvent(gender, agecategory, weightcategory, kind)
                        if kind == "TOTAL":
                            _events = _event.get_events()
                            if _events[0].total > _current_record.value:
                                _current_record.event = _events[0]
                                _current_record.value = _events[0].total
                                _current_record.save()
                        else:
                            _attempts = _event.get_attempts()
                            # if (
                            #     weightcategory.weight == "44"
                            #     and agecategory == "U17"
                            #     and gender == "female"
                            # ):
                            #     for toto in _attempts:
                            #         ic(toto.__dict__)
                            if (
                                _attempts[0].value > _current_record.value
                                and _attempts[0].name == kind
                                and _attempts[0].validate == 1
                            ):
                                _current_record.event = _attempts[0].event
                                _current_record.value = _attempts[0].value
                                _current_record.save()
        ic("Simple record - finished")

        ic("SENIOR Treatment - start")

        treatment_senior = TreatmentSenior()
        ic("SENIOR: set_record_from_other_agecategories - start")
        treatment_senior.set_record_from_other_agecategories("U20")
        ic("SENIOR: set_record_from_other_agecategories - finished")

        ic("SENIOR Treatment - finished")

        ic("U20 Treatment - start")

        treatment_u20 = TreatmentU20()
        ic("U20: set_record_from_other_agecategories - start")
        treatment_u20.set_record_from_other_agecategories("U17")
        ic("U20: set_record_from_other_agecategories - finished")

        ic("U20: set_record_from_last_agecategory - start")
        treatment_u20.set_record_from_last_agecategory()
        ic("U20: set_record_from_last_agecategory - finsihed")

        ic("U20 Treatment - finished")

        ic("U17 Treatment - start")

        treatment_u17 = TreatmentU17()
        ic("U17: set_record_from_other_agecategories - start")
        treatment_u17.set_record_from_other_agecategories("U15")
        ic("U17: set_record_from_other_agecategories - finished")

        ic("U17: set_record_from_last_agecategory - start")
        treatment_u17.set_record_from_last_agecategory()
        ic("U17: set_record_from_last_agecategory - finsihed")

        ic("U17 Treatment - finished")

        ic("U15 Treatment - start")

        treatment_u15 = TreatmentU15()
        ic("U15: set_record_from_other_agecategories - start")
        # treatment_u17.set_record_from_other_agecategories("U15")
        ic("U15: set_record_from_other_agecategories - finished")

        ic("U15: set_record_from_last_agecategory - start")
        treatment_u15.set_record_from_last_agecategory()
        ic("U15: set_record_from_last_agecategory - finsihed")

        ic("U15 Treatment - finished")
