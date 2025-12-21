import datetime
import itertools
import math
from decimal import Decimal
from functools import total_ordering
from operator import attrgetter, itemgetter, methodcaller

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max, Min, Q, Sum
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import html, timezone
from django.utils.safestring import mark_safe


# Create your models here.
class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Wallpaper(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    wallpaper = models.ImageField(upload_to="wallpapers")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Gender(Post):
    name = models.CharField(max_length=255)
    verbosename = models.CharField(max_length=255)
    value = models.IntegerField()

    class Meta:
        db_table = "gender"
        verbose_name = "Genre"

    def __str__(self):
        return self.verbosename


class Season(Post):
    name = models.CharField(max_length=255, unique=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    preseason_id = models.IntegerField(default=0)

    class Meta:
        db_table = "season"
        verbose_name = "Saison"
        ordering = [
            "start_date",
        ]

    def __str__(self):
        return self.name


class Competitionkind(Post):
    name = models.CharField(max_length=255)
    # gender = models.ForeignKey(Gender, on_delete=models.CASCADE)

    class Meta:
        db_table = "competitionkind"
        verbose_name = "Type de compétition"
        ordering = [
            "name",
        ]

    def __str__(self):
        return self.name


class Competition(Post):
    def __init__(self, *args, **kwargs):
        super(Competition, self).__init__(*args, **kwargs)
        self._can_begin = False
        self._has_begun = False
        self._has_ended = False

    name = models.CharField(max_length=255, verbose_name="Nom")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="Saison")
    isteam = models.BooleanField(default=False, verbose_name="Equipe")
    ismasters = models.BooleanField(default=False, verbose_name="Masters")
    isminime = models.BooleanField(default=False, verbose_name="Minime")
    kind = models.ForeignKey(
        Competitionkind, on_delete=models.CASCADE, verbose_name="Type", null=True
    )
    place = models.CharField(max_length=255, verbose_name="Lieu")
    address = models.CharField(max_length=255, verbose_name="Adresse")
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, verbose_name="Genre")
    troop = models.IntegerField(verbose_name="Nombre de participants max")
    countevents = models.IntegerField(
        default=0, verbose_name="Nombre de participants inscrits"
    )
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    closed = models.BooleanField(default=False, verbose_name="Clos")
    visibility = models.BooleanField(default=True, verbose_name="Visibilité")
    isrecordeligible = models.BooleanField(
        default=False, verbose_name="Eligible aux records"
    )

    class Meta:
        db_table = "competition"
        verbose_name = "Compétition"
        # ordering = ['start_date', ]

    def __str__(self):
        return self.name

    def teamIWFSorted(self):
        def sortIWF(team):
            return team.iwf

        teamList = list(self.team_set.all())
        teamList.sort(key=sortIWF, reverse=True)

        return teamList

    @property
    def can_begin(self):
        if self.leader_set.filter(leadertype__name="Arbitre 1"):
            self._can_begin = True

        if self.leader_set.filter(leadertype__name="Jury 1"):
            self._can_begin = True
        return self._can_begin

    @property
    def has_begun(self):
        self._has_begun = any([event.has_begun for event in self.event_set.all()])
        return self._has_begun

    @property
    def has_ended(self):
        self._has_ended = all([event.has_ended for event in self.event_set.all()])
        return self._has_ended

    @property
    def is_exceeded(self):
        is_exceeded = False
        if self.start_date < datetime.date.today():
            is_exceeded = True
        return is_exceeded


class Agecategory(Post):
    name = models.CharField(max_length=255, verbose_name="Nom")
    surname = models.CharField(max_length=255, default="", verbose_name="Détail")
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, verbose_name="Genre")
    agemin = models.IntegerField(verbose_name="Age min.")
    agemax = models.IntegerField(verbose_name="Age max.")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="Saison")

    class Meta:
        db_table = "agecategory"
        verbose_name = "Catégorie"
        ordering = ["agemin", "gender", "name"]

    def __str__(self):
        return self.name


class Weightcategory(Post):
    agecategory = models.ForeignKey(
        Agecategory, on_delete=models.CASCADE, verbose_name="catégorie d'âge"
    )
    weight = models.CharField(max_length=5, verbose_name="Poids en kg")

    class Meta:
        db_table = "weightcategory"
        verbose_name = "Catégories de poids"
        verbose_name_plural = "Catégories de poids"
        ordering = ["id", "agecategory", "weight"]

    def __str__(self):
        return self.weight

    def changeform_link(self):
        if self.id:
            changeform_url = reverse("admin:api_weightcategory_change", args=(self.id,))
            return mark_safe('<a href="%s">Séries</a>' % changeform_url)
        return ""

    changeform_link.allow_tags = True
    changeform_link.short_description = ""


class Minimumweightcategory(Post):
    name = models.CharField(max_length=255, verbose_name="Nom")
    weight = models.IntegerField(verbose_name="Poids en kg")
    weightcategory = models.ForeignKey(
        Weightcategory, on_delete=models.CASCADE, verbose_name="minima"
    )

    class Meta:
        db_table = "minimumweightcategory"
        verbose_name = "Minimun par catégories de poids"
        ordering = ("id",)

    def __str__(self):
        return str(self.weight)


class Concurrent(Post):
    ffhmfacUser = models.IntegerField(unique=True, null=True)
    ffhmfacClub = models.IntegerField(null=True)
    clubName = models.CharField(max_length=255, null=True)
    licence = models.CharField(max_length=255, null=True)
    firstname = models.CharField(max_length=255, null=True)
    lastname = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True)
    date_of_birth = models.DateTimeField(null=True)

    class Meta:
        db_table = "concurrent"
        verbose_name = "Athlète"

    def __str__(self):
        return self.licence


class Leadertype(Post):
    name = models.CharField(max_length=255, default="")
    view_order = models.IntegerField(default=0)

    class Meta:
        db_table = "leadertype"

    def __str__(self):
        return self.name


class Leader(Post):
    concurrent = models.ForeignKey(Concurrent, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    leadertype = models.ForeignKey(Leadertype, on_delete=models.CASCADE)

    class Meta:
        db_table = "leader"
        verbose_name = "Dirigeant"

    def __str__(self):
        return self.leadertype.name


class Team(Post):
    name = models.CharField(max_length=255)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    draw = models.IntegerField(default=0)

    class Meta:
        db_table = "team"
        verbose_name = "Equipe"
        ordering = [
            "draw",
        ]

    def __str__(self):
        return self.name

    @property
    def iwf(self):
        def truncate(number, digits) -> float:
            stepper = pow(10.0, digits)
            return math.trunc(stepper * number) / stepper

        iwf = 0.0
        for event in self.event_set.all():
            iwf = iwf + event.iwf

        return truncate(iwf, 2)


class Profile(Post):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    licence = models.CharField(max_length=255, null=True, blank=True)
    club = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "profile"


@total_ordering
class Event(Post):
    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self._has_begun = False
        self._has_ended = False

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    ffhmfacClub = models.IntegerField(null=True)
    clubName = models.CharField(max_length=255, null=True)
    concurrent = models.ForeignKey(Concurrent, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
    draw = models.IntegerField(default=0)
    weight = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    weightcategory = models.ForeignKey(
        Weightcategory, null=True, on_delete=models.CASCADE
    )
    agecategory = models.ForeignKey(Agecategory, null=True, on_delete=models.CASCADE)
    minimumweightcategory = models.ForeignKey(
        Minimumweightcategory, null=True, on_delete=models.CASCADE
    )
    total = models.IntegerField(default=0)
    iwf = models.FloatField(default=0)

    class Meta:
        db_table = "event"
        verbose_name = "Evènement"
        ordering = [
            "id",
        ]

    @property
    def has_begun(self):
        self._has_begun = any(
            [
                True if attempt.validate > 0 else False
                for attempt in self.attempt_set.all()
            ]
        )
        return self._has_begun

    @property
    def has_ended(self):
        self._has_ended = all(
            [
                True if attempt.validate > 0 else False
                for attempt in self.attempt_set.all()
            ]
        )
        return self._has_ended

    def categorie(self):
        return self.concurrent.gender.name[:1].upper()

    def __eq__(self, other):
        return False

    def __hash__(self):
        return hash(self.pk)

    def __lt__(self, other):
        isLower = True

        try:
            selfAttempt = self.attempt_set.filter(name="ARR", validate=0, value__gt=0)[
                :1
            ].get()
        except Attempt.DoesNotExist:
            selfAttempt = None

        try:
            otherAttempt = other.attempt_set.filter(
                name="ARR", validate=0, value__gt=0
            )[:1].get()
        except Attempt.DoesNotExist:
            otherAttempt = None

        if selfAttempt is None and otherAttempt is None:
            try:
                selfAttempt = self.attempt_set.filter(
                    name="EP-J", validate=0, value__gt=0
                )[:1].get()
            except Attempt.DoesNotExist:
                selfAttempt = None

            try:
                otherAttempt = other.attempt_set.filter(
                    name="EP-J", validate=0, value__gt=0
                )[:1].get()
            except Attempt.DoesNotExist:
                otherAttempt = None

        if selfAttempt is not None and otherAttempt is not None:
            if not selfAttempt.event.competition.isminime:
                if self.concurrent.gender_id == 2 and other.concurrent.gender_id == 3:
                    return False
                elif self.concurrent.gender_id == 3 and other.concurrent.gender_id == 2:
                    return True

            if selfAttempt.value < otherAttempt.value:
                isLower = True
            elif selfAttempt.value == otherAttempt.value:
                if selfAttempt.rank < otherAttempt.rank:
                    isLower = True
                elif selfAttempt.rank == otherAttempt.rank:
                    if selfAttempt.distance < otherAttempt.distance:
                        isLower = True
                    elif selfAttempt.distance == otherAttempt.distance:
                        selfTotal = (
                            self.attempt_set.filter(
                                name=selfAttempt.name, rank__lt=selfAttempt.rank
                            ).aggregate(Sum("value"))["value__sum"]
                            or 0
                        )
                        otherTotal = (
                            other.attempt_set.filter(
                                name=otherAttempt.name, rank__lt=selfAttempt.rank
                            ).aggregate(Sum("value"))["value__sum"]
                            or 0
                        )
                        if selfTotal < otherTotal:
                            isLower = True
                        elif selfTotal == otherTotal:
                            if selfAttempt.event.competition.isteam:
                                if (
                                    selfAttempt.event.team.draw
                                    < otherAttempt.event.team.draw
                                ):
                                    isLower = True
                                else:
                                    isLower = False
                            else:
                                if selfAttempt.event.draw < otherAttempt.event.draw:
                                    isLower = True
                                else:
                                    isLower = False
                        else:
                            isLower = False
                    else:
                        isLower = False
                else:
                    isLower = False
            else:
                isLower = False
        elif selfAttempt is None and otherAttempt is not None:
            isLower = False
        elif selfAttempt is None and otherAttempt is None:
            # selfTotal = self.attempt_set.filter(validate=1).aggregate(Sum('value'))['value__sum'] or 0
            # otherTotal = other.attempt_set.filter(validate=1).aggregate(Sum('value'))['value__sum'] or 0
            selfTotal = self.totalSet[0] + self.totalSet[1]
            otherTotal = other.totalSet[0] + other.totalSet[1]
            if selfTotal > otherTotal:
                isLower = True
            elif selfTotal == otherTotal:
                if self.totalSet[1] < other.totalSet[1]:
                    isLower = True
                else:
                    isLower = False
            else:
                isLower = False

        return isLower

    @property
    def totalSet(self):
        listTotal = []
        listTotal.append(0)
        listTotal.append(0)

        # if self.competition.isminime:
        if self.agecategory.name == "U10" or self.agecategory.name == "U13":
            if self.attempt_set.filter(name="ARR", validate=1).count() > 1:
                listTotal[0] = (
                    self.attempt_set.filter(name="ARR", validate=1).aggregate(
                        Sum("value")
                    )["value__sum"]
                    or 0
                )
            if self.competition.isteam:
                listTotal[0] = (
                    self.attempt_set.filter(name="ARR", validate=1).aggregate(
                        Sum("value")
                    )["value__sum"]
                    or 0
                )

            if self.attempt_set.filter(name="EP-J", validate=1).count() > 1:
                listTotal[1] = (
                    self.attempt_set.filter(name="EP-J", validate=1).aggregate(
                        Sum("value")
                    )["value__sum"]
                    or 0
                )
            if self.competition.isteam:
                listTotal[1] = (
                    self.attempt_set.filter(name="EP-J", validate=1).aggregate(
                        Sum("value")
                    )["value__sum"]
                    or 0
                )

            if self.attempt_set.filter(name="ARR", validate=1).count() == 3:
                listTotal[0] = (
                    listTotal[0]
                    - self.attempt_set.filter(name="ARR", validate=1).aggregate(
                        Min("value")
                    )["value__min"]
                )

            if self.attempt_set.filter(name="EP-J", validate=1).count() == 3:
                listTotal[1] = (
                    listTotal[1]
                    - self.attempt_set.filter(name="EP-J", validate=1).aggregate(
                        Min("value")
                    )["value__min"]
                )
        else:
            listTotal[0] = (
                self.attempt_set.filter(name="ARR", validate=1).aggregate(Max("value"))[
                    "value__max"
                ]
                or 0
            )
            listTotal[1] = (
                self.attempt_set.filter(name="EP-J", validate=1).aggregate(
                    Max("value")
                )["value__max"]
                or 0
            )

        # listTotal[0] = 25
        if self.competition.isteam:
            # listTotal[0] = self.attempt_set.filter(name='ARR', validate=1).aggregate(Max('value'))['value__max'] or 0
            # listTotal[1] = self.attempt_set.filter(name='EP-J', validate=1).aggregate(Max('value'))['value__max'] or 0
            self.total = listTotal[0] + listTotal[1]
            if (
                self.attempt_set.filter(validate=1, name="ARR").count() > 0
                or self.attempt_set.filter(validate=2, name="EP-J").count() > 0
            ):
                self.total = listTotal[0] + listTotal[1]
        else:
            if (
                self.attempt_set.filter(validate=1, name="EP-J").count() > 0
                or self.attempt_set.filter(validate=2, name="EP-J").count() > 0
            ):
                self.total = listTotal[0] + listTotal[1]
                if listTotal[0] == 0 or listTotal[1] == 0:
                    self.total = 0
        return listTotal

    @property
    def firstARRAttemptNotValidate(self):
        attempt = (
            self.attempt_set.all()
            .filter(validate=0, name="ARR")
            .order_by("rank")
            .first()
        )
        return attempt

    @property
    def firstEPJAttemptNotValidate(self):
        attempt = (
            self.attempt_set.all()
            .filter(validate=0, name="EP-J")
            .order_by("rank")
            .first()
        )
        return attempt

    @property
    def getARRAttemptSet(self):
        return self.attempt_set.all().filter(name="ARR")

    @property
    def getEPJAttemptSet(self):
        return self.attempt_set.all().filter(name="EP-J")


class Attempt(Post):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)
    validate = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    distance = models.IntegerField(default=0)

    class Meta:
        db_table = "attempt"
        verbose_name = "Tentative"
        ordering = [
            "name",
            "rank",
        ]

    def __str__(self):
        return self.name

    @property
    def editable(self):
        editable = True
        if self.validate > 0:
            editable = False
        return editable


class Region(Post):
    name = models.CharField(max_length=255)
    short = models.CharField(max_length=255)


class RecordStandard(models.Model):
    arr = models.IntegerField(default=0, verbose_name="Arraché")
    ep_j = models.IntegerField(default=0, verbose_name="Epaulé jeté")
    AGE_CATEGORIES = {
        "SENIOR": "SENIOR",
        "U20": "U20",
        "U15": "U15",
        "U17": "U17",
    }
    weightcategory = models.CharField(
        max_length=5, verbose_name="Catégorie de poids de corps"
    )
    agecategory = models.CharField(
        max_length=7, choices=AGE_CATEGORIES, verbose_name="Catégorie d'âge"
    )
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="Saison")
    gender = models.ForeignKey(
        Gender, on_delete=models.CASCADE, null=True, verbose_name="Genre"
    )

    class Meta:
        db_table = "record_standard"
        verbose_name = "Standard Record de France"
        verbose_name_plural = "Standards Record de France"

    @property
    def total(self):
        return self.arr + self.ep_j


class Record(models.Model):
    AGE_CATEGORIES = {
        "SENIOR": "SENIOR",
        "U20": "U20",
        "U15": "U15",
        "U17": "U17",
    }
    ATTEMPT_KINDS = {"ARR": "ARR", "EP-J": "EP-J", "TOTAL": "TOTAL"}
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        limit_choices_to={"competition__isrecordeligible": True},
        null=True,
    )
    kind = models.CharField(max_length=5, choices=ATTEMPT_KINDS, null=True, blank=True)
    agecategory = models.CharField(
        max_length=7,
        choices=AGE_CATEGORIES,
        null=True,
        blank=True,
        verbose_name="Catégorie d'âge",
    )
    weightcategory = models.CharField(
        max_length=5, null=True, blank=True, verbose_name="Catégorie de poids de corps"
    )
    gender = models.ForeignKey(
        Gender, on_delete=models.CASCADE, null=True, verbose_name="Genre"
    )
    value = models.IntegerField(default=0)
    is_current = models.BooleanField(default=False, verbose_name="Record en cours")

    class Meta:
        db_table = "record"
        verbose_name = "Record de France"
        verbose_name_plural = "Records de France"
