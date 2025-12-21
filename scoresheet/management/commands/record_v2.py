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
from scoresheet.views.utils import ManageRecords


class Command(BaseCommand):
    def get_record_standard(self, gender, agecategory, weightcategory):
        record_standard = RecordStandard.objects.get(
            gender__name=gender, agecategory=agecategory, weightcategory=weightcategory
        )

        return record_standard

    def get_record(self, gender, agecategory, weightcategory, kind):
        record = Record.objects.get(
            gender__name=gender,
            agecategory=agecategory,
            weightcategory=weightcategory,
            kind=kind,
        )

        return record

    def handle(self, *args, **options):
        record_manager = ManageRecords()
        record_list = Record.objects.all()
        nb_record = record_list.count()
        genders = ["male", "female"]
        agecategories = ["SENIOR", "U20", "U17", "U15"]
        kinds = ["ARR", "EP-J", "TOTAL"]
        current_season = list(Season.objects.all().order_by("-id"))[0]
        for gender in genders:
            for agecategory in agecategories:
                weightcategories = Weightcategory.objects.filter(
                    agecategory__name=agecategory,
                    agecategory__gender__name=gender,
                    agecategory__season=current_season,
                ).order_by("weight")
                for kind in kinds:
                    ic(gender, agecategory, kind)
                    for weightcategory in weightcategories:
                        ic(weightcategory.weight)
                        try:
                            current_record = self.get_record(
                                gender, agecategory, weightcategory, kind
                            )
                        except Record.DoesNotExist:
                            current_record_standard = self.get_record_standard(
                                gender, agecategory, weightcategory
                            )
                            new_record = Record()
                            new_record.weightcategory = weightcategory.weight
                            new_record.kind = kind
                            new_record.agecategory = agecategory
                            new_record.gender = Gender.objects.get(name=gender)
                            if kind == "ARR":
                                new_record.value = current_record_standard.arr
                            if kind == "EP-J":
                                new_record.value = current_record_standard.ep_j
                            if kind == "TOTAL":
                                new_record.value = (
                                    current_record_standard.ep_j
                                    + current_record_standard.arr
                                )
                            new_record.save()
                            current_record = new_record

                        attempts = (
                            Attempt.objects.prefetch_related("event")
                            .filter(
                                event__competition__isrecordeligible=True,
                                # event__weightcategory__weight=weightcategory.weight,
                                event__agecategory__name=agecategory,
                                name=kind,
                                validate=1,
                                event__competition__gender__name=gender,
                                event__concurrent__country="FR",
                            )
                            .order_by("rank", "updated_at")
                        )
                        for attempt in attempts:
                            current_weight = attempt.event.weightcategory.weight
                            # current_agecategory = attempt.event.agecategory.name
                            if attempt.event.competition.season.pk != current_season.pk:
                                buffer_event = record_manager.set_weightcategory(
                                    attempt.event
                                )
                                current_weight = buffer_event.weightcategory.weight
                                # if (
                                #     current_weight != weightcategory.weight
                                # ) or current_agecategory != agecategory:
                                #     continue
                            if current_weight != weightcategory.weight:
                                continue
                            if attempt.value > current_record.value or (
                                attempt.value >= current_record.value
                                and not current_record.event
                            ):
                                current_record.value = attempt.value
                                current_record.event = attempt.event
                                current_record.save()
                        if kind == "TOTAL":
                            attempts = (
                                Attempt.objects.prefetch_related("event")
                                .filter(
                                    event__competition__isrecordeligible=True,
                                    # event__weightcategory__weight=weightcategory.weight,
                                    event__agecategory__name=agecategory,
                                    validate=1,
                                    event__competition__gender__name=gender,
                                    event__concurrent__country="FR",
                                )
                                .order_by("rank", "updated_at")
                            )
                            for attempt in attempts:
                                current_weight = attempt.event.weightcategory.weight
                                if (
                                    attempt.event.competition.season.id
                                    != current_season.id
                                ):
                                    buffer_event = record_manager.set_weightcategory(
                                        attempt.event
                                    )
                                    current_weight = buffer_event.weightcategory.weight
                                if current_weight != weightcategory.weight:
                                    continue
                                if attempt.event.total > current_record.value or (
                                    attempt.event.total >= current_record.value
                                    and not current_record.event
                                ):
                                    current_record.value = attempt.event.total
                                    current_record.event = attempt.event
                                    current_record.save()

        for record in Record.objects.all():
            if not record.event:
                continue
            if record.agecategory == "U15":
                continue
            buffer_event = record_manager.get_last_agecategory(record.event)
            if not buffer_event:
                continue
            if buffer_event.agecategory.id == record.event.agecategory.id:
                continue

            try:
                current_record = self.get_record(
                    record.gender.name,
                    buffer_event.agecategory.name,
                    record.weightcategory,
                    record.kind,
                )
            except Record.DoesNotExist:
                continue

            if record.value > current_record.value:
                current_record.value = record.value
                current_record.event = record.event
                current_record.save()

        for record in Record.objects.all():
            buffer_agecategories = ["U15", "U17", "U20", "SENIOR"]
            if not record.event:
                continue
            if record.agecategory == "SENIOR":
                continue
            # ic(record.agecategory)
            # ic(
            #    buffer_agecategories[
            #        buffer_agecategories.index(record.agecategory) + 1 :
            #    ]
            # )
            for age in buffer_agecategories[
                buffer_agecategories.index(record.agecategory) + 1 :
            ]:
                try:
                    current_record = self.get_record(
                        record.gender.name,
                        age,
                        record.weightcategory,
                        record.kind,
                    )
                except Record.DoesNotExist:
                    continue
                if record.value > current_record.value:
                    current_record.value = record.value
                    current_record.event = record.event
                    current_record.save()
