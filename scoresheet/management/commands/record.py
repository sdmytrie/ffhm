from django.core.management.base import BaseCommand

from api.models import (
    Agecategory,
    Attempt,
    Concurrent,
    Event,
    Record,
    RecordStandard,
    Season,
    Weightcategory,
    Gender,
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

    def get_last_agecategory_by_season(self, name, gender):
        return Agecategory.objects.get(
            season=self.get_current_season(), name=name, gender=gender
        )

    def get_current_season(self):
        season_list = Season.objects.all().order_by("-end_date")
        return season_list[0]

    def get_gender(self, name):
        return Gender.objects.get(name=name)

    def handle(self, *args, **options):
        age_categories = ["U15", "U17", "U20", "SENIOR"]
        for gender in ["male", "female"]:
            for attempt_type in ["ARR", "EP-J", "TOTAL"]:
                for age in age_categories:

                    current_agecategory = self.get_last_agecategory_by_season(
                        age, self.get_gender(gender)
                    )
                    for weightcategory in current_agecategory.weightcategory_set.all():
                        print(gender, age, weightcategory)
                        if attempt_type == "TOTAL":
                            attempt_all = Event.objects.filter(
                                agecategory=current_agecategory,
                                weightcategory=weightcategory,
                                competition__isrecordeligible=True,
                                competition__gender=self.get_gender(gender),
                                concurrent__country="FR",
                            ).order_by("-total", "updated_at")
                            for buffer_attempt in attempt_all:
                                buffer_attempt.weightcategory = self.get_weightcategory(
                                    buffer_attempt
                                )
                        else:
                            attempt_all = Attempt.objects.filter(
                                event__agecategory=current_agecategory,
                                # event__weightcategory=weightcategory,
                                event__competition__isrecordeligible=True,
                                event__competition__gender=self.get_gender(gender),
                                event__concurrent__country="FR",
                                name=attempt_type,
                                validate=1,
                            ).order_by("-value", "updated_at")
                            for buffer_attempt in attempt_all:
                                buffer_attempt.weightcategory = self.get_weightcategory(
                                    buffer_attempt.event
                                )
                            attempt_all = list(
                                filter(
                                    lambda x: x.weightcategory.weight
                                    == weightcategory.weight,
                                    attempt_all,
                                )
                            )
                        record_standard_all = RecordStandard.objects.filter(
                            weightcategory=weightcategory.weight,
                            agecategory__in=age_categories[age_categories.index(age) :],
                            gender=self.get_gender(gender),
                        )
                        try:
                            for record_standard in record_standard_all:
                                record_standard_value = {
                                    "ARR": record_standard.arr,
                                    "EP-J": record_standard.ep_j,
                                    "TOTAL": record_standard.arr + record_standard.ep_j,
                                }
                                if attempt_type == "TOTAL":
                                    attempt_value = attempt_all[0].total
                                else:
                                    attempt_value = attempt_all[0].value
                                if attempt_value > record_standard_value[attempt_type]:
                                    arr = False
                                    ep_j = False
                                    total = False
                                    if attempt_type == "ARR":
                                        arr = True
                                    elif attempt_type == "EP-J":
                                        ep_j = True
                                    else:
                                        total = True
                                    try:
                                        record = Record.objects.get(
                                            event__agecategory=current_agecategory,
                                            event__weightcategory=weightcategory,
                                            event__competition__gender=self.get_gender(
                                                gender
                                            ),
                                            arr=arr,
                                            ep_j=ep_j,
                                            total=total,
                                        )
                                    except Record.DoesNotExist:
                                        record = Record()
                                    record.arr = arr
                                    record.ep_j = ep_j
                                    record.total = total
                                    record.is_current = True
                                    if attempt_type == "TOTAL":
                                        record.event = attempt_all[0]
                                    else:
                                        record.event = attempt_all[0].event
                                    record.save()
                        except Exception as e:
                            ic(f"error: {e}")
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
