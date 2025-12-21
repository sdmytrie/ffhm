from django.core.management.base import BaseCommand
from icecream import ic

from api.models import (
    Agecategory,
    Attempt,
    Concurrent,
    Event,
    Record,
    RecordStandard,
    Season,
    Weightcategory,
)
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
                event__pk=event.pk,
                # event__agecategory__name=event.agecategory.name,
                # event__weightcategory__weight=event.weightcategory.weight,
                # event__concurrent__gender__pk=event.concurrent.gender.pk,
                is_current=True,
            )
        )
        result = False
        for current_record in current_records:
            if (
                (attempt_name == "arr" and current_record.arr)
                or (attempt_name == "ep_j" and current_record.ep_j)
                or (attempt_name == "total" and current_record.total)
            ):
                result = True
                # if attempt_name == "ep_j" and current_record.ep_j:
                #     result = True
                # if attempt_name == "total" and current_record.total:
                #     result = True
        return result

    def handle(self, *args, **options):
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

        standard_all = RecordStandard.objects.all()

        for event in event_list:
            arr, ep_j = event.totalSet
            total = arr + ep_j

            try:
                current_record = RecordStandard.objects.get(
                    agecategory=event.agecategory.name,
                    weightcategory=event.weightcategory.weight,
                    gender__pk=event.concurrent.gender.pk,
                )
                if arr >= current_record.arr:
                    # ic(current_record.__dict__)
                    try:
                        buffer = Record.objects.get(
                            arr=True,
                            event__weightcategory__weight=current_record.weightcategory,
                            event__agecategory__name=current_record.agecategory,
                            event__competition__gender=current_record.gender,
                        )
                    except Record.DoesNotExist:
                        buffer = Record()
                        buffer.arr = True
                        buffer.is_current = True
                        buffer.event = event
                        buffer.save()
                if ep_j >= current_record.ep_j:
                    try:
                        buffer = Record.objects.get(
                            ep_j=True,
                            event__weightcategory__weight=current_record.weightcategory,
                            event__agecategory__name=current_record.agecategory,
                            event__competition__gender=current_record.gender,
                        )
                    except Record.DoesNotExist:
                        buffer = Record()
                        buffer.ep_j = True
                        buffer.is_current = True
                        buffer.event = event
                        buffer.save()
                if total >= current_record.total:
                    try:
                        buffer = Record.objects.get(
                            total=True,
                            event__weightcategory__weight=current_record.weightcategory,
                            event__agecategory__name=current_record.agecategory,
                            event__competition__gender=current_record.gender,
                        )
                    except Record.DoesNotExist:
                        buffer = Record()
                        buffer.total = True
                        buffer.is_current = True
                        buffer.event = event
                        buffer.save()
                buffer = None
            except Exception as e:
                pass
            ## try:
        for event in event_list:
            arr, ep_j = event.totalSet
            total = arr + ep_j
            current_records = list(
                Record.objects.prefetch_related("event").filter(
                    event__agecategory__name=event.agecategory.name,
                    event__weightcategory__weight=event.weightcategory.weight,
                    event__concurrent__gender__pk=event.concurrent.gender.pk,
                    is_current=True,
                )
            )
            for current_record in current_records:
                current_arr, current_ep_j = current_record.event.totalSet
                if arr > current_arr and current_record.arr:
                    current_record.event = event
                    current_record.save()
                elif arr == current_arr and current_record.arr:
                    attempt = list(
                        Attempt.objects.filter(
                            event=event, validate=2, name="ARR", value=arr
                        ).order_by("-rank")
                    )
                    attempt_record = list(
                        Attempt.objects.filter(
                            event=current_record.event,
                            validate=2,
                            name="ARR",
                            value=current_arr,
                        ).order_by("-rank")
                    )
                    if (
                        len(attempt) > 0
                        and len(attempt_record) > 0
                        and attempt[0].updated_at < attempt_record[0].updated_at
                    ):
                        current_record.event = event
                        current_record.save()

                if ep_j > current_ep_j and current_record.ep_j:
                    current_record.event = event
                    current_record.save()
                elif ep_j == current_ep_j and current_record.ep_j:
                    attempt = list(
                        Attempt.objects.filter(
                            event=event, validate=2, name="EP-J", value=arr
                        ).order_by("-rank")
                    )
                    attempt_record = list(
                        Attempt.objects.filter(
                            event=current_record.event,
                            validate=2,
                            name="EP-J",
                            value=current_arr,
                        ).order_by("-rank")
                    )
                    if (
                        len(attempt) > 0
                        and len(attempt_record) > 0
                        and attempt[0].updated_at < attempt_record[0].updated_at
                    ):
                        current_record.event = event
                        current_record.save()

                if total > current_arr + current_ep_j and current_record.total:
                    current_record.event = event
                    current_record.save()
