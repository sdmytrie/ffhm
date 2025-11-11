"""
    ATTEMPT
"""
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import redirect

from api.models import Attempt, Record, RecordStandard
from scoresheet.views.utils import iwf


@permission_required('scoresheet.change_attempt')
def attempt_change(request, value, attempt_id):
    """ change attempt """

    attempt = Attempt.objects.get(id=attempt_id)

    for rank in range(attempt.rank, 3):
        attempt_buffer = Attempt.objects.get(
            event_id=attempt.event.id, name=attempt.name, rank=rank+1
        )
        attempt_buffer.value = 0
        attempt_buffer.validate = 0
        if int(value) == 0:
            attempt_buffer.validate = 2
        attempt_buffer.save()

    if attempt.rank > 1:
        attempt_buffer = Attempt.objects.get(
            event_id=attempt.event.id, name=attempt.name, rank=attempt.rank-1
        )
        if attempt.event.agecategory.name == 'U10' or attempt.event.agecategory.name == 'U13':
            maxValue = attempt_buffer.value + 2

        if int(attempt_buffer.value) > int(value) and int(value) > 0:
            if attempt_buffer.validate == 1:
                value = int(attempt_buffer.value) + 1
            else:
                value = int(attempt_buffer.value)

    if (attempt.event.agecategory.name == 'U10' or attempt.event.agecategory.name == 'U13') and attempt.rank > 1:
        attempt.value = min(int(value), maxValue)
    else:
        attempt.value = value

    attempt.validate = 0
    if int(value) == 0:
        attempt.validate = 2

    if attempt.rank == 3:
        attempt_buffer = Attempt.objects.get(
            event_id=attempt.event.id, name=attempt.name, rank=2)
        if attempt_buffer.value == 0:
            return HttpResponse()

    attempt.save()

    return HttpResponse()


@permission_required('scoresheet.change_attempt')
def attempt_validate(request, value, attempt_id):
    """ validate attempt """

    attempt = Attempt.objects.get(id=attempt_id)

    if attempt.event.competition.isminime:
        if attempt.rank == 1 or value == "0":
            attempt.validate = value
        else:
            if attempt.distance < -2:
                attempt.validate = 2
            else:
                attempt.validate = value
    else:
        attempt.validate = value

    if attempt.rank < 3:
        attempt2 = Attempt.objects.get(
            event_id=attempt.event_id, name=attempt.name, rank=attempt.rank+1)
        if value == "1":
            attempt2.value = attempt.value + 1
        elif value == "2":
            attempt2.value = attempt.value
        attempt.validate = value
        attempt.save()
        attempt2.save()
        attempt2.event.iwf = iwf(attempt.event)
        attempt2.event.save()

    attempt.save()

    if attempt.event.competition.isteam == True:
        attempt.event.total = attempt.event.totalSet[0] + \
            attempt.event.totalSet[1]
    else:
        attempt.event.total = 0

    attempt.event.save()
    attempt.event.iwf = iwf(attempt.event)
    attempt.event.save()

    if attempt.event.competition.isrecordeligible and attempt.event.concurrent.country == "FR":
        buffer = {"arr": False,
                  "ep_j": False,
                  "total": False
                  }
        if attempt.name == "ARR":
            buffer["arr"] = True
        if attempt.name == "EP-J":
            buffer["ep_j"] = True
        try:
            record = Record.objects.get(
                event__weightcategory__weight=attempt.event.weightcategory.weight,
                event__concurrent__gender__value=attempt.event.concurrent.gender.value,
                event__agecategory__name=attempt.event.agecategory.name,
                arr=buffer["arr"],
                ep_j=buffer["ep_j"],
                is_current=1
            )
            if attempt.name == "ARR" and attempt.value > record.event.totalSet[1] and attempt.validate == "1":
                current_record = Record()
                current_record.event = attempt.event
                current_record.arr = True
                current_record.is_current = True
                current_record.save()
                record.is_current = False
                record.save()
            if attempt.name == "EP-J" and attempt.value > record.event.totalSet[0] and attempt.validate == "1":
                current_record = Record()
                current_record.event = attempt.event
                current_record.ep_j = True
                current_record.is_current = True
                current_record.save()
                record.is_current = False
                record.save()
            record = Record.objects.get(
                event__weightcategory__weight=attempt.event.weightcategory.weight,
                event__concurrent__gender__value=attempt.event.concurrent.gender.value,
                event__agecategory__name=attempt.event.agecategory.name,
                total=True,
                is_current=1
            )
            if attempt.event.total > record.event.total:
                current_record = Record()
                current_record.event = attempt.event
                current_record.total = True
                current_record.is_current = True
                current_record.save()
                record.is_current = False
                record.save()
        except:
            record = RecordStandard.objects.get(
                agecategory=attempt.event.agecategory.name,
                weightcategory=attempt.event.weightcategory.weight,
                gender__id=attempt.event.concurrent.gender.id
            )
            if attempt.name == "ARR" and attempt.value > record.arr and attempt.validate == "1":
                current_record = Record()
                current_record.event = attempt.event
                current_record.arr = True
                current_record.is_current = True
                current_record.save()
            if attempt.name == "EP-J" and attempt.value > record.ep_j and attempt.validate == "1":
                current_record = Record()
                current_record.event = attempt.event
                current_record.ep_j = True
                current_record.is_current = True
                current_record.save()
            if attempt.event.total > record.total:
                current_record = Record()
                current_record.event = attempt.event
                current_record.total = True
                current_record.is_current = True
                current_record.save()

    if attempt.event.competition.isteam:
        return redirect('scoresheet:team_competition_view', str(attempt.event.competition.id))
    return redirect('scoresheet:competition_view', str(attempt.event.competition.id))
