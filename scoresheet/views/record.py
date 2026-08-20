from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from icecream import ic

from api.models import (
    Agecategory,
    Attempt,
    Event,
    Record,
    RecordStandard,
    Season,
    Weightcategory,
)
from scoresheet.management.commands.lib.weightcategory import FfhmWeightcategory
from scoresheet.views import agecategory, concurrent
from scoresheet.views.utils import ManageRecords


def get_records(age, gender):
    pass


@user_passes_test(lambda u: u.is_superuser)
def record_delete(request, id):
    record = Record.objects.get(pk=id)
    record_standard = RecordStandard.objects.get(
        weightcategory=record.weightcategory,
        agecategory=record.agecategory,
        gender=record.gender,
    )
    record.event = None
    if record.kind == "ARR":
        record.value = record_standard.arr
    elif record.kind == "EP-J":
        record.value = record_standard.ep_j
    elif record.kind == "TOTAL":
        record.value = record_standard.total
    record.save()
    return redirect("scoresheet:record")


@user_passes_test(lambda u: u.is_superuser)
def record_edit(request, id):
    _all_agecategories = ["SENIOR", "U20", "U17", "U15"]
    _kind_title = {"ARR": "Arraché", "EP-J": "Ep/jeté", "TOTAL": "total"}
    record = Record.objects.get(pk=id)
    record_standard = RecordStandard.objects.get(
        weightcategory=record.weightcategory,
        agecategory=record.agecategory,
        gender=record.gender,
    )
    _ffhm_weightcategory = FfhmWeightcategory()
    _min_weight, _max_weight = _ffhm_weightcategory.get_range(
        record.gender.name, record.agecategory, record.weightcategory
    )
    _value = {
        "ARR": record_standard.arr,
        "EP-J": record_standard.ep_j,
        "TOTAL": record_standard.total,
    }
    _all_valid_agecategories = _all_agecategories
    if record.agecategory != "SENIOR":
        _all_valid_agecategories = _all_agecategories[
            _all_agecategories.index(record.agecategory) - 1 :
        ]
    _events = []
    if record.kind != "TOTAL":
        _attempts = Attempt.objects.filter(
            event__weight__gt=_min_weight,
            event__weight__lte=_max_weight,
            event__agecategory__name__in=_all_valid_agecategories,
            event__concurrent__gender=record.gender,
            event__concurrent__country="FR",
            event__competition__isrecordeligible=True,
            validate=1,
            name=record.kind,
            value__gte=_value[record.kind],
        ).order_by("-value", "updated_at")
    else:
        _attempts = Attempt.objects.filter(
            event__weight__gt=_min_weight,
            event__weight__lte=_max_weight,
            event__agecategory__name__in=_all_valid_agecategories,
            event__concurrent__gender=record.gender,
            event__concurrent__country="FR",
            event__competition__isrecordeligible=True,
            event__total__gte=_value[record.kind],
        ).order_by("-value", "updated_at")

    for attempt in _attempts:
        _exists = any(event.pk == attempt.event.pk for event in _events)
        if not _exists:
            _agecategory = Agecategory.objects.get(
                name=record.agecategory,
                season=record.event.competition.season,
                gender=record.event.concurrent.gender,
            )
            current_season = list(
                Season.objects.all().order_by("start_date").reverse()
            )[0]
            _age = (
                current_season.start_date.year
                - attempt.event.concurrent.date_of_birth.year
            ) + 1
            if _age >= _agecategory.agemin and _age <= _agecategory.agemax:
                if attempt.event.agecategory.name != record.agecategory:
                    if attempt.updated_at.year == current_season.end_date.year:
                        continue
                _events.append(attempt.event)

    content = {
        "record": record,
        "kind_title": _kind_title[record.kind],
        "record_standard": record_standard,
        "value_reference": _value[record.kind],
        "all_agecategories": " ".join(_all_valid_agecategories),
        "min_weight": _min_weight,
        "max_weight": _max_weight,
        "events": _events,
    }

    return render(request, "scoresheet/record/edit.html", content)


# @cache_page(60 * 60 * 24, key_prefix="record_list")
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
                record_arr = Record.objects.get(
                    weightcategory=weight,
                    agecategory=key,
                    gender__value=gender_id,
                    kind="ARR",
                )
                record_ep_j = Record.objects.get(
                    weightcategory=weight,
                    agecategory=key,
                    gender__value=gender_id,
                    kind="EP-J",
                )
                record_total = Record.objects.get(
                    weightcategory=weight,
                    agecategory=key,
                    gender__value=gender_id,
                    kind="TOTAL",
                )
                buffer["arr"] = {"value": record_arr.value, "event": record_arr.event}
                buffer["arr"]["id"] = record_arr.pk
                buffer["ep_j"] = {
                    "value": record_ep_j.value,
                    "event": record_ep_j.event,
                }
                buffer["ep_j"]["id"] = record_ep_j.pk
                buffer["total"] = {
                    "value": record_total.value,
                    "event": record_total.event,
                }
                buffer["total"]["id"] = record_total.pk

                all_ages = ["SENIOR", "U20", "U17", "U15"]
                buffer_ages = all_ages[all_ages.index(key) :]

                # records_event = list(
                #     Record.objects.filter(
                #         # event__weightcategory__weight=weight,
                #         event__concurrent__gender__value=gender_id,
                #         event__agecategory__name__in=buffer_ages,
                #         is_current=True,
                #     )
                # )
                records[key][gender_name].append(buffer)

    return render(request, "scoresheet/record/record.html", locals())
