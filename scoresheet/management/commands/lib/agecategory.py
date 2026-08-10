from copy import deepcopy

from api.models import Agecategory, Event, Season


class FfhmAgecategory:
    def get_last_agecategory(self, event: Event) -> Event | None:
        age = (
            event.competition.season.end_date.year - event.concurrent.date_of_birth.year
        )
        current_season = list(Season.objects.order_by("-id").all())

        agecategoryList = list(
            Agecategory.objects.filter(
                season=event.competition.season,
                gender=event.concurrent.gender,
            )
            .exclude(name__startswith="M")
            .exclude(name__startswith="W")
            .order_by("agemin")
        )

        current = agecategoryList[0]
        new_event = None
        existing_agecategory = ["SENIOR", "U20", "U17", "U15"]
        for agecategory in agecategoryList:
            if age - 1 <= current.agemax:
                if (
                    event.agecategory.name != current.name
                    and event.updated_at.year == current_season[0].start_date.year
                    and current.name in existing_agecategory
                ):
                    new_event = deepcopy(event)
                    new_event.agecategory = current
                break
            current = agecategory
        return new_event
