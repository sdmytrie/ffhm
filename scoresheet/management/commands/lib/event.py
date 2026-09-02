from datetime import datetime

from api.models import Attempt, Competition, Event, Season, Weightcategory
from scoresheet.management.commands.lib.weightcategory import FfhmWeightcategory


class FfhmEvent:
    def __init__(
        self,
        gender: str,
        agecategory: str,
        weightcategory: Weightcategory,
        kind: str,
    ) -> None:
        self.gender = gender
        self.agecategory = agecategory
        self.weightcategory = weightcategory
        self.kind = kind
        self._season = list(Season.objects.all().order_by("-id"))[0]
        self._reference_date = datetime.strptime(
            "2026-09-01 00:00:00", "%Y-%m-%d %H:%M:%S"
        )

    @property
    def season(self):
        return self._season

    @season.setter
    def season(self, value: Season):
        self._season = value

    def get_attempts(self):
        _ffhm_weightcategory = FfhmWeightcategory()
        min, max = _ffhm_weightcategory.get_range(
            self.gender, self.agecategory, self.weightcategory.weight
        )
        _attempts = Attempt.objects.filter(
            name=self.kind,
            event__agecategory__name=self.agecategory,
            # event__weightcategory__weight=self.weightcategory.weight,
            event__weight__gt=min,
            event__weight__lte=max,
            event__concurrent__gender__name=self.gender,
            # event__competition__season=self.season,
            event__competition__isrecordeligible=True,
            event__competition__start_date__gt=self._reference_date,
            event__concurrent__country="FR",
            validate=1,
        ).order_by("-value", "updated_at")

        return _attempts

    def get_events(self):
        _ffhm_weightcategory = FfhmWeightcategory()
        min, max = _ffhm_weightcategory.get_range(
            self.gender, self.agecategory, self.weightcategory.weight
        )
        _events = Event.objects.filter(
            agecategory__name=self.agecategory,
            # weightcategory__weight=self.weightcategory.weight,
            weight__gt=min,
            weight__lte=max,
            concurrent__gender__name=self.gender,
            # competition__season=self.season,
            competition__isrecordeligible=True,
            competition__start_date__gt=self._reference_date,
            concurrent__country="FR",
        ).order_by("-total", "updated_at")

        return _events
