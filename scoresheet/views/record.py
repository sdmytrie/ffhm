from django.shortcuts import render
from django.urls import reverse

from api.models import (
    Concurrent,
    Event,
    Agecategory,
    Record,
    RecordStandard,
    Season,
    Weightcategory,
)
from icecream import ic
from scoresheet.views.utils import ManageRecords


def get_records(age, gender):
    pass


def record(request, season_id="0"):
    page = "record"

    current_season = list(Season.objects.all().order_by("start_date").reverse())[0]
    if season_id == "0":
        season = current_season
    else:
        season = Season.objects.get(id=season_id)
    season_url_value = reverse("scoresheet:record")

    records = {
        "SENIOR": {"Féminin": [], "Masculin": []},
        "U20": {"Féminin": [], "Masculin": []},
        "U17": {"Féminin": [], "Masculin": []},
        "U15": {"Féminin": [], "Masculin": []},
    }

    weight_categories = []
    buffer = {}
    record_manager = ManageRecords()
    for gender_name, gender_id in {"Masculin": "1", "Féminin": "2"}.items():
        for key, _ in records.items():
            weight_categories = list(
                Weightcategory.objects.filter(
                    agecategory__name=key,
                    agecategory__gender__value=gender_id,
                    agecategory__season__pk=season.pk,
                ).all()
            )
            for weight in weight_categories:
                buffer = {"weight": weight}
                record_standard = RecordStandard.objects.get(
                    weightcategory=weight, agecategory=key
                )
                buffer["arr"] = {
                    "value": record_standard.arr,
                    "concurrent": "standard",
                    "is_standard": True,
                }
                buffer["ep_j"] = {
                    "value": record_standard.ep_j,
                    "concurrent": "standard",
                    "is_standard": True,
                }
                buffer["total"] = {
                    "value": record_standard.total,
                    "concurrent": "standard",
                    "is_standard": True,
                }

                all_ages = ["SENIOR", "U20", "U17", "U15"]
                buffer_ages = all_ages[all_ages.index(key) :]

                records_event = list(
                    Record.objects.filter(
                        # event__weightcategory__weight=weight,
                        event__concurrent__gender__value=gender_id,
                        event__agecategory__name__in=buffer_ages,
                        is_current=True,
                    )
                )
                if records_event:
                    for record_event in records_event:
                        if (
                            record_manager.set_weightcategory(
                                record_event.event
                            ).weightcategory.weight
                            != weight.weight
                        ):
                            continue
                        if record_event.arr:
                            if (
                                buffer["arr"]["is_standard"]
                                and record_event.event.totalSet[0]
                                >= buffer["arr"]["value"]
                            ) or record_event.event.totalSet[0] > buffer["arr"][
                                "value"
                            ]:
                                buffer["arr"] = {
                                    "value": record_event.event.totalSet[0],
                                    "concurrent": record_event.event.concurrent,
                                    "is_standard": False,
                                }
                        if record_event.ep_j:
                            if (
                                buffer["ep_j"]["is_standard"]
                                and record_event.event.totalSet[1]
                                >= buffer["ep_j"]["value"]
                            ) or record_event.event.totalSet[1] > buffer["arr"][
                                "value"
                            ]:
                                buffer["ep_j"] = {
                                    "value": record_event.event.totalSet[1],
                                    "concurrent": record_event.event.concurrent,
                                    "is_standard": False,
                                }
                        if record_event.total:
                            if (
                                buffer["total"]["is_standard"]
                                and record_event.event.total >= buffer["total"]["value"]
                            ) or record_event.event.total > buffer["arr"]["value"]:
                                buffer["total"] = {
                                    "value": record_event.event.total,
                                    "concurrent": record_event.event.concurrent,
                                    "is_standard": False,
                                }
                else:
                    records_event = None
                    buffer["arr"] = {
                        "value": record_standard.arr,
                        "concurrent": "standard",
                        "is_standard": True,
                    }
                    buffer["ep_j"] = {
                        "value": record_standard.ep_j,
                        "concurrent": "standard",
                        "is_standard": True,
                    }
                    buffer["total"] = {
                        "value": record_standard.total,
                        "concurrent": "standard",
                        "is_standard": True,
                    }
                records[key][gender_name].append(buffer)

        # weight_categories = list(
        #     Weightcategory.objects.filter(
        #         agecategory__name=key,
        #         agecategory__gender__value=2,
        #         agecategory__season__pk=season.pk,
        #     ).all()
        # )
        # for weight in weight_categories:
        #     buffer = {"weight": weight}
        #     record_standard = RecordStandard.objects.get(
        #         weightcategory=weight, agecategory=key
        #     )
        #     buffer["arr"] = {
        #         "value": record_standard.arr,
        #         "concurrent": "standard",
        #         "is_standard": True,
        #     }
        #     buffer["ep_j"] = {
        #         "value": record_standard.ep_j,
        #         "concurrent": "standard",
        #         "is_standard": True,
        #     }
        #     buffer["total"] = {
        #         "value": record_standard.total,
        #         "concurrent": "standard",
        #         "is_standard": True,
        #     }

        #     all_ages = ["SENIOR", "U20", "U17", "U15"]
        #     buffer_ages = all_ages[all_ages.index(key) :]
        #     records_event = list(
        #         Record.objects.filter(
        #             # event__weightcategory__weight=weight,
        #             event__concurrent__gender__value=2,
        #             event__agecategory__name__in=buffer_ages,
        #             is_current=True,
        #         )
        #     )
        #     if records_event:
        #         for record_event in records_event:
        #             if (
        #                 record_manager.set_weightcategory(
        #                     record_event.event
        #                 ).weightcategory.weight
        #                 != weight.weight
        #             ):
        #                 continue
        #             if record_event.arr:
        #                 if record_event.event.totalSet[0] > buffer["arr"]["value"]:
        #                     buffer["arr"] = {
        #                         "value": record_event.event.totalSet[0],
        #                         "concurrent": record_event.event.concurrent,
        #                         "is_standard": False,
        #                     }
        #             if record_event.ep_j:
        #                 if record_event.event.totalSet[1] > buffer["ep_j"]["value"]:
        #                     buffer["ep_j"] = {
        #                         "value": record_event.event.totalSet[1],
        #                         "concurrent": record_event.event.concurrent,
        #                         "is_standard": False,
        #                     }
        #             if record_event.total:
        #                 if record_event.event.total > buffer["total"]["value"]:
        #                     buffer["total"] = {
        #                         "value": record_event.event.total,
        #                         "concurrent": record_event.event.concurrent,
        #                         "is_standard": False,
        #                     }
        #     else:
        #         records_event = None
        #         buffer["arr"] = {
        #             "value": record_standard.arr,
        #             "concurrent": "standard",
        #             "is_standard": True,
        #         }
        #         buffer["ep_j"] = {
        #             "value": record_standard.ep_j,
        #             "concurrent": "standard",
        #             "is_standard": True,
        #         }
        #         buffer["total"] = {
        #             "value": record_standard.total,
        #             "concurrent": "standard",
        #             "is_standard": True,
        #         }
        #     records[key]["Féminin"].append(buffer)

    return render(request, "scoresheet/record/record.html", locals())
