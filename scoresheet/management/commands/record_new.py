from django.core.management.base import BaseCommand

from api.models import (
    Agecategory,
    Competition,
    Concurrent,
    Event,
    Gender,
    Record,
    RecordStandard,
    Season,
    Weightcategory,
)
from icecream import ic
from scoresheet.views.utils import ManageRecords


class Command(BaseCommand):
    def get_weightcategory(self, event):
        current_weightcategoryList = []
        current_weightcategory = None
        current_season = list(Season.objects.order_by("-id").all())
        current_agecategory = Agecategory.objects.get(
            name=event.agecategory.name,
            season=current_season[0],
            gender=event.competition.gender,
        )
        if float(event.weight) == 0.0 or event.agecategory.name == "U10":
            current_weightcategory = None
        else:
            weightcategoryList = list(
                Weightcategory.objects.filter(agecategory_id=current_agecategory.id)
            )
            for weightcategory in weightcategoryList:
                if ">" in weightcategory.weight:
                    max_weightcategory = weightcategory
                    continue
                current_weightcategoryList.append(weightcategory)

            current_weightcategoryList.sort(key=lambda w: float(w.weight))
            current = weightcategoryList[0]

            for weightcategory in current_weightcategoryList:
                if float(event.weight) <= float(current.weight):
                    current_weightcategory = current
                    break
                current = weightcategory

            current_max_weightcategory = current_weightcategoryList[-1]
            if not current_weightcategory:
                current_weightcategory = current_max_weightcategory

            if float(event.weight) > float(current_max_weightcategory.weight):
                current_weightcategory = max_weightcategory
        return current_weightcategory

    def record_exists(self, event, attempt_name):
        current_records = list(
            Record.objects.filter(
                event__agecategory__name=event.agecategory.name,
                event__weightcategory__weight=event.weightcategory.weight,
                event__concurrent__gender__pk=event.concurrent.gender.pk,
                is_current=True,
            )
        )
        for current_record in current_records:
            if attempt_name == "arr" and current_record.arr:
                return True
            if attempt_name == "ep_j" and current_record.ep_j:
                return True
            if attempt_name == "total" and current_record.total:
                return True
        return False

    def get_current_season(self):
        season_list = Season.objects.all().order_by("-end_date")
        return season_list[0]

    def get_last_agecategory_by_season(self, name, gender):
        return Agecategory.objects.get(
            season=self.get_current_season(), name=name, gender=gender
        )

    def get_gender(self, name):
        return Gender.objects.get(name=name)

    def get_records_by_agecategory_and_weightcategory(
        self, agecategory, weightcategory
    ):
        return Record.objects.filter(
            event__agecategory=agecategory, event__weightcategory=weightcategory
        )

    def get_records_by_agecategory_and_weightcategory_and_attempt_name(
        self, agecategory, weightcategory, attempt_name
    ):
        attempt = {"arr": False, "ep_j": False, "total": False}
        attempt[attempt_name.lower()] = True
        ic(attempt)
        return Record.objects.get(
            event__agecategory=agecategory,
            event__weightcategory=weightcategory,
            is_current=True,
            arr=attempt["arr"],
            ep_j=attempt["ep_j"],
            total=attempt["total"],
        )

    def get_events_by_agecategory_and_weightcategory(self, agecategory, weightcategory):
        return Event.objects.filter(
            competition__isrecordeligible=True,
            competition__season=self.get_current_season(),
            agecategory=agecategory,
            weightcategory=weightcategory,
        )

    def get_events_by_agecategory_and_weightcategory_and_attempt_name(
        self, agecategory, weightcategory, attempt_name
    ):
        return Event.objects.filter(
            competition__isrecordeligible=True,
            competition__season=self.get_current_season(),
            agecategory=agecategory,
            weightcategory=weightcategory,
            attempt__name=attempt_name,
        ).order_by("attempt__updated_at")

    def handle(self, *args, **options):
        age_categories = ["U15", "U17", "U20", "SENIOR"]
        print(age_categories)
        current_agecategory = self.get_last_agecategory_by_season(
            "U17", self.get_gender("male")
        )
        for weightcategory in current_agecategory.weightcategory_set.all():
            try:
                print(weightcategory)
                current_record = (
                    self.get_records_by_agecategory_and_weightcategory_and_attempt_name(
                        current_agecategory, weightcategory, "arr"
                    )
                )
                print(current_record)
                for attempt in current_record.event.attempt_set.all():
                    value = 0
                    if attempt.name.lower() == "arr" and attempt.validate == 1:
                        if attempt.value > value:
                            current_attempt = attempt
                ic(current_attempt.value)
                ic(current_attempt.validate)
                ic(current_attempt.updated_at)

                # ic(
                #    self.get_events_by_agecategory_and_weightcategory_and_attempt_name(
                #        current_agecategory, weightcategory, "arr"
                #    )
                # )
            except Record.DoesNotExist:
                print("No Record")

        return

        record_manager = ManageRecords()
        record_list = Record.objects.all()
        for record in record_list:
            record.delete()

        event_list = []
        buffer_event_list = []
        # buffer_event_list = map(
        #    record_manager.set_weightcategory, record_manager.get_events()
        # )
        for event in record_manager.get_events():
            buffer_event_list.append(event)
            new_event = record_manager.get_last_agecategory(event)
            if new_event:
                buffer_event_list.append(new_event)

        event_list = list(map(record_manager.set_weightcategory, buffer_event_list))
        event_list.sort(key=lambda x: x.updated_at)

        for event in event_list:
            arr, ep_j = event.totalSet
            total = arr + ep_j

            try:
                current_record = RecordStandard.objects.get(
                    agecategory=event.agecategory.name,
                    weightcategory=event.weightcategory.weight,
                    gender__pk=event.concurrent.gender.pk,
                )
                if arr >= current_record.arr and not self.record_exists(event, "arr"):
                    new_record = Record()
                    new_record.event = event
                    new_record.is_current = True
                    new_record.arr = True
                    new_record.save()
                if ep_j >= current_record.ep_j and not self.record_exists(
                    event, "ep_j"
                ):
                    new_record = Record()
                    new_record.event = event
                    new_record.is_current = True
                    new_record.ep_j = True
                    new_record.save()
                if (
                    total >= current_record.arr + current_record.ep_j
                    and not self.record_exists(event, "total")
                ):
                    new_record = Record()
                    new_record.event = event
                    new_record.is_current = True
                    new_record.total = True
                    new_record.save()
                new_record = None
            except Exception as e:
                pass
            ## try:
            current_records = list(
                Record.objects.filter(
                    event__agecategory__name=event.agecategory.name,
                    event__weightcategory__weight=event.weightcategory.weight,
                    event__concurrent__gender__pk=event.concurrent.gender.pk,
                    is_current=True,
                )
            )
            for current_record in current_records:
                current_arr, current_ep_j = current_record.event.totalSet
                if arr > current_arr and current_record.arr:
                    current_record.is_current = False
                    current_record.save()
                    new_record = Record()
                    new_record.event = event
                    new_record.is_current = True
                    new_record.arr = True
                    new_record.save()

                elif ep_j > current_ep_j and current_record.ep_j:
                    current_record.is_current = False
                    current_record.save()
                    new_record = Record()
                    new_record.event = event
                    new_record.is_current = True
                    new_record.ep_j = True
                    new_record.save()

                elif total > current_arr + current_ep_j and current_record.total:
                    current_record.is_current = False
                    current_record.save()
                    new_record = Record()
                    new_record.event = event
                    new_record.is_current = True
                    new_record.total = True
                    new_record.save()
                new_record = None
