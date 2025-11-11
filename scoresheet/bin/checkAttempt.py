from django.db.utils import *

from scoresheet.models import *

# attemptSet = Attempt.objects.all()
# for attempt in attemptSet:
#     attempt.save()
#     attempt.event.save()

eventSet = Event.objects.all()
for event in eventSet:
    event.minimumweightcategory = None
    event.save()
    if event.agecategory.name != "U10":
        minimumweightcategoryList = list(event.weightcategory.minimumweightcategory_set.all().order_by('weight'))
        current = None
        for minimumweightcategory in minimumweightcategoryList:
            if event.total < minimumweightcategory.weight:
                event.minimumweightcategory = current
                event.save()
                break
            current = minimumweightcategory

    #     if not event.minimumweightcategory:
    #         event.minimumweightcategory = minimumweightcategoryList[-1]

    event.save()