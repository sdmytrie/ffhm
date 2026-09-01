from icecream import ic

from api.models import Agecategory, Event, Record
from scoresheet.management.commands.lib.agecategory import FfhmAgecategory
from scoresheet.management.commands.lib.record import FfhmRecord
from scoresheet.management.commands.lib.treatment import Treatment


class TreatmentU17(Treatment):
    def __init__(self) -> None:
        super().__init__()

    def set_record_from_other_agecategories(self, agecategory: str):
        for gender in super().genders:
            for kind in super().kinds:
                _all_records = Record.objects.filter(
                    agecategory="U17", gender=gender, kind=kind
                )
                for record in _all_records:
                    _buffer_weightcategory = record.weightcategory
                    if (
                        record.weightcategory == "95" or record.weightcategory == ">95"
                    ) and gender.name == "male":
                        _buffer_weightcategory = ">85"
                    elif (
                        record.weightcategory == "77" or record.weightcategory == ">77"
                    ) and gender.name == "female":
                        _buffer_weightcategory = ">69"
                    _buffer_record = Record.objects.get(
                        agecategory=agecategory,
                        gender=gender,
                        kind=kind,
                        weightcategory=_buffer_weightcategory,
                    )
                    if kind == "TOTAL":
                        if not _buffer_record.event:
                            pass
                        elif not record.event:
                            if _buffer_record.event.total >= record.value:
                                record.value = _buffer_record.value
                                record.event = _buffer_record.event
                                record.save()
                        else:
                            if _buffer_record.event.total > record.value:
                                record.value = _buffer_record.value
                                record.event = _buffer_record.event
                                record.save()
                    else:
                        if not record.event:
                            if _buffer_record.value >= record.value:
                                record.value = _buffer_record.value
                                record.event = _buffer_record.event
                                record.save()
                        else:
                            if (
                                _buffer_record.value >= record.value
                                and _buffer_record.event.updated_at
                                < record.event.updated_at
                            ):
                                record.value = _buffer_record.value
                                record.event = _buffer_record.event
                                record.save()

    def set_record_from_last_agecategory(self):
        for gender in super().genders:
            _current_agecategory = Agecategory.objects.get(
                name="U20", season=super().current_season, gender__name=gender.name
            )
            _last_agecategory = Agecategory.objects.get(
                name="U17", season=super().last_season, gender__name=gender.name
            )
            _events = Event.objects.prefetch_related("concurrent").filter(
                competition__isrecordeligible=True,
                concurrent__country="FR",
                agecategory=_current_agecategory,
            )
            for event in _events:
                _age = (
                    event.competition.season.end_date.year
                    - event.concurrent.date_of_birth.year
                )
                if _age - 1 > _last_agecategory.agemax:
                    continue
                for kind in super().kinds:
                    _ffhm_record = FfhmRecord(gender.name, "U17", None, kind)
                    if (
                        event.weightcategory.weight == "86"
                        or event.weightcategory.weight == ">86"
                    ) and gender.name == "female":
                        _ffhm_record.weight = ">77"
                    elif (
                        event.weightcategory.weight == "110"
                        or event.weightcategory.weight == ">110"
                    ) and gender.name == "male":
                        _ffhm_record.weight = ">95"
                    else:
                        _ffhm_record.weight = event.weightcategory.weight
                    _current_record = _ffhm_record.get_record()
                    if _current_record:
                        for attempt in event.attempt_set.all():
                            if (
                                attempt.updated_at.year
                                >= super().current_season.end_date.year
                            ):
                                continue
                            if attempt.validate > 1:
                                continue
                            if kind == "TOTAL":
                                if event.total > _current_record.value:
                                    _current_record.event = event
                                    _current_record.value = event.total
                                    _current_record.save()
                            else:
                                if _current_record.event:
                                    if (
                                        attempt.value > _current_record.value
                                        and attempt.name == kind
                                    ):
                                        _current_record.value = attempt.value
                                        _current_record.event = event
                                        _current_record.save()
                                    elif (
                                        attempt.value == _current_record.value
                                        and attempt.updated_at
                                        < _current_record.event.updated_at
                                        and attempt.name == kind
                                    ):
                                        _current_record.value = attempt.value
                                        _current_record.event = event
                                        _current_record.save()
                                else:
                                    if (
                                        attempt.value >= _current_record.value
                                        and attempt.name == kind
                                    ):
                                        _current_record.value = attempt.value
                                        _current_record.event = event
                                        _current_record.save()
