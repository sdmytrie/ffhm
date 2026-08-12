from icecream import ic

from api.models import Record
from scoresheet.management.commands.lib.record import FfhmRecord
from scoresheet.management.commands.lib.treatment import Treatment


class TreatmentSenior(Treatment):
    def __init__(self) -> None:
        super().__init__()

    def set_record_from_other_agecategories(self, agecategory: str):
        for gender in super().genders:
            for kind in super().kinds:
                _all_records = Record.objects.filter(
                    agecategory="SENIOR", gender=gender, kind=kind
                )
                for record in _all_records:
                    _buffer_record = Record.objects.get(
                        agecategory="U20",
                        gender=gender,
                        kind=kind,
                        weightcategory=record.weightcategory,
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
                            if _buffer_record.value > record.value:
                                record.value = _buffer_record.value
                                record.event = _buffer_record.event
                                record.save()
