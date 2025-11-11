# exec(open('scoresheet/bin/migrate.py').read())
from django.db.models import Q
from django.db.utils import *

from api.models import *

concurrents = Concurrent.objects.all()

i = 0
for concurrent in concurrents:
    if int(concurrent.licence) == concurrent.ffhmfacUser:
        buffer_concurrents = Concurrent.objects.exclude(
            ffhmfacUser=concurrent.licence
        ).filter(licence=concurrent.licence)
        for old in buffer_concurrents:
            i = i + 1
            new_id = concurrent.pk
            print("new: " + concurrent.licence + ":" + str(new_id))
            print("old: " + old.licence + ":" + str(old.pk))
            print("old events: " + str(len(old.event_set.all())))
            for event in old.event_set.all():
                event.concurrent = concurrent
                event.save()
            old.delete()
            print(concurrent.lastname + ":" + old.lastname)
            print()
            # for current in buffer_concurrents:
            # print(current.lastname)

print(i)

i = 0
for concurrent in concurrents:
    if (
        len(concurrent.event_set.all()) == 0
        and concurrent.ffhmfacUser == concurrent.licence
    ):
        i = i + 1
        print(concurrent.lastname + " " + concurrent.licence)

print(i)

i = 0
for concurrent in concurrents:
    buffer_concurrents = Concurrent.objects.exclude(pk=concurrent.pk).filter(
        licence=concurrent.licence
    )
    for dbl in buffer_concurrents:
        i = i + 1
        print(dbl.lastname + " " + dbl.licence)

print(i)
