from api.models import Attempt, Event, Season, Weightcategory


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

    @property
    def season(self):
        return self._season

    @season.setter
    def season(self, value: Season):
        self._season = value

    def get_attempts(self):
        _attempts = Attempt.objects.filter(
            name=self.kind,
            event__agecategory__name=self.agecategory,
            event__weightcategory=self.weightcategory,
            event__competition__gender__name=self.gender,
            event__competition__season=self.season,
            event__competition__isrecordeligible=True,
            event__concurrent__country="FR",
            validate=1,
        ).order_by("-value", "updated_at")

        return _attempts

    def get_events(self):
        _attempts = Event.objects.filter(
            agecategory__name=self.agecategory,
            weightcategory=self.weightcategory,
            competition__gender__name=self.gender,
            competition__season=self.season,
            competition__isrecordeligible=True,
            concurrent__country="FR",
        ).order_by("-total", "updated_at")

        return _attempts
