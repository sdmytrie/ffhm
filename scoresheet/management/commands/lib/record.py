from django.core.cache import cache

from api.models import (
    Agecategory,
    Gender,
    Record,
    RecordStandard,
    Season,
    Weightcategory,
)


class FfhmRecord:
    def __init__(
        self,
        gender: str,
        agecategory: str,
        weightcategory: Weightcategory,
        kind: str,
    ) -> None:
        self.gender = gender
        self.agecategory = agecategory
        self.weight = "0"
        self.weightcategory = None
        if weightcategory:
            self.weightcategory = weightcategory
            self.weight = self.weightcategory.weight
        self.kind = kind
        self.season = list(Season.objects.all().order_by("-id"))[0]

    def get_record_standard(self):
        _record_standard = RecordStandard.objects.get(
            gender__name=self.gender,
            agecategory=self.agecategory,
            weightcategory=self.weight,
            season=self.season,
        )

        return _record_standard

    def get_record(self):
        try:
            _record = Record.objects.get(
                gender__name=self.gender,
                agecategory=self.agecategory,
                weightcategory=self.weight,
                kind=self.kind,
            )
            return _record
        except Exception as error:
            print(error)

    def get_and_create_record(self):
        try:
            _record = Record.objects.get(
                gender__name=self.gender,
                agecategory=self.agecategory,
                weightcategory=self.weight,
                kind=self.kind,
            )
            return _record
        except Record.DoesNotExist:
            _record_standard = self.get_record_standard()

            _new_record = Record()
            _new_record.weightcategory = self.weight
            _new_record.kind = self.kind
            _new_record.agecategory = self.agecategory
            _new_record.gender = Gender.objects.get(name=self.gender)
            if self.kind == "ARR":
                _new_record.value = _record_standard.arr
            elif self.kind == "EP-J":
                _new_record.value = _record_standard.ep_j
            elif self.kind == "TOTAL":
                _new_record.value = _record_standard.ep_j + _record_standard.arr

            _new_record.save()
            return _new_record
