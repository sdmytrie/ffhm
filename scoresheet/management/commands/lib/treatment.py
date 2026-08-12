from api.models import Gender, Season


class Treatment:
    def __init__(self) -> None:
        self._genders = Gender.objects.filter(value__gt=0)
        self._seasons = list(Season.objects.all().order_by("-id"))
        self._kinds = ["ARR", "EP-J", "TOTAL"]

    @property
    def genders(self):
        return self._genders

    @genders.setter
    def genders(self, value: Gender):
        self._genders = value

    @property
    def current_season(self):
        return self._seasons[0]

    @property
    def last_season(self):
        return self._seasons[1]

    @property
    def kinds(self):
        return self._kinds
