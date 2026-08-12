from icecream import ic

from api.models import Season, Weightcategory


class FfhmWeightcategory:
    def __init__(self) -> None:
        self._season = list(Season.objects.all().order_by("-id"))[0]

    def get_range(self, gender: str, agecategory: str, weight: str):
        _weightcategories = list(
            Weightcategory.objects.filter(
                agecategory__season=self._season,
                agecategory__name=agecategory,
                agecategory__gender__name=gender,
            )
            .order_by("weight")
            .values_list("weight", flat=True)
        )
        _weightcategories.insert(0, "0")
        _weightcategories.pop()
        _weightcategories = [int(x) for x in _weightcategories]
        _weightcategories.sort()
        for weightcatory in _weightcategories:
            if ">" in weight:
                max = 1000
                min = int(weight.replace(">", ""))
            else:
                max = int(weight)
                min = _weightcategories[_weightcategories.index(int(weight)) - 1]
        return min, max
