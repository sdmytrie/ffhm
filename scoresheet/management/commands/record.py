from django.core.management.base import BaseCommand

from api.models import Agecategory, Concurrent, Event, Record, RecordStandard, Season, Weightcategory
from icecream import ic


class Command(BaseCommand):
    def get_weightcategory(self, event):
        current_weightcategoryList = []
        current_weightcategory = None
        current_season = list(Season.objects.order_by("-id").all())
        current_agecategory = Agecategory.objects.get(name=event.agecategory.name, season=current_season[0], gender=event.competition.gender)
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
        current_records = list(Record.objects.filter(
            event__agecategory__name=event.agecategory.name,
            event__weightcategory__weight=event.weightcategory.weight,
            event__concurrent__gender__pk=event.concurrent.gender.pk,
            is_current=True,
        ))
        for current_record in current_records:
            if attempt_name == "arr" and current_record.arr:
                return True
            if attempt_name == "ep_j" and current_record.ep_j:
                return True
            if attempt_name == "total" and current_record.total:
                return True
        return False

    def handle(self, *args, **options):
        record_list = Record.objects.all()
        for record in record_list:
            record.delete()

        event_list = list(Event.objects.filter(competition__isrecordeligible=True, competition__closed=True, competition__isminime=False, concurrent__country="FR").all())
        event_list.sort(key=lambda x: x.updated_at)

        for event in event_list:
            weightcategory = self.get_weightcategory(event)
            event.weightcategory = weightcategory
            arr, ep_j = event.totalSet
            total = arr + ep_j

            current_record = RecordStandard.objects.get(
                agecategory=event.agecategory.name,
                weightcategory=event.weightcategory.weight,
                gender__pk=event.concurrent.gender.pk
            )
            if arr > current_record.arr and not self.record_exists(event, "arr"):
                new_record = Record()
                new_record.event = event
                new_record.is_current = True
                new_record.arr = True
                new_record.save()
            if ep_j > current_record.ep_j and not self.record_exists(event, "ep_j"):
                new_record = Record()
                new_record.event = event
                new_record.is_current = True
                new_record.ep_j = True
                new_record.save()
            if total > current_record.arr + current_record.ep_j and not self.record_exists(event, "total"):
                new_record = Record()
                new_record.event = event
                new_record.is_current = True
                new_record.total = True
                new_record.save()
            new_record = None
            # try:
            current_records = list(Record.objects.filter(
                event__agecategory__name=event.agecategory.name,
                event__weightcategory__weight=event.weightcategory.weight,
                event__concurrent__gender__pk=event.concurrent.gender.pk,
                is_current=True,
            ))
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

