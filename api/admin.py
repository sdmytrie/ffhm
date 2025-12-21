from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.html import format_html_join

# from .models import Choice, Question, Competition, Competitionkind
from django.http import HttpResponseRedirect

from .models import *

# Register your models here.


admin.site.site_header = "Administration de scoresheet"


class EventInline(admin.TabularInline):
    model = Event


class SeasonAdmin(admin.ModelAdmin):
    model = Event
    exclude = ("preseason_id",)


class competitionkindAdmin(admin.ModelAdmin):
    model = Competitionkind


class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "season",
        "visibility",
        "gender",
        "kind",
        "isteam",
        "place",
        "isrecordeligible",
    )
    list_filter = (
        "season",
        "visibility",
        "gender",
        "isteam",
        "isrecordeligible",
        "kind",
    )
    date_hierarchy = "updated_at"
    ordering = (
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)

    def response_change(self, request, obj):
        res = super(CompetitionAdmin, self).response_change(request, obj)
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET["next"])
        else:
            return res

    def response_add(self, request, obj):
        res = super(CompetitionAdmin, self).response_add(request, obj)
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET["next"])
        else:
            return res

    # inlines = [EventInline]


class MinimumweightcategoryInline(admin.TabularInline):
    model = Minimumweightcategory


class WeightcategoryAdmin(admin.ModelAdmin):
    list_display = (
        "agecategory",
        "gender",
        "weight",
    )
    list_filter = ("agecategory",)
    ordering = ("weight",)
    search_fields = ("agecategory",)

    def gender(self, weightcategory):
        # agegategory = Agecategory.objects.filter(id=weightcategory.agegategory.id)
        return weightcategory.agecategory.gender.name

    def response_change(self, request, obj):
        res = super(WeightcategoryAdmin, self).response_change(request, obj)
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET["next"])
        else:
            return res

    gender.short_description = "Genre"

    inlines = [MinimumweightcategoryInline]


class LeadertypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "view_order",
    )
    list_filter = (
        "name",
        "view_order",
    )
    ordering = ("view_order",)
    search_fields = ("name",)


class MinimumweightcategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "weight", "agecategory")
    ordering = ("id",)

    # search_fields = ('agecategory', )

    def agecategory(self, minimumweightcategory):
        agecategory = Agecategory.objects.get(
            id=minimumweightcategory.weightcategory.agecategory.id
        )
        return agecategory


class WeightcategoryInline(admin.TabularInline):
    model = Weightcategory
    fields = ("weight", "changeform_link")
    readonly_fields = ("changeform_link",)


class AgecategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "surname",
        "gender",
        "agemin",
        "agemax",
        "weightcategoryList",
        "season",
    )
    list_filter = (
        "season",
        "gender",
        "name",
    )
    ordering = (
        "gender",
        "agemin",
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "surname",
    )

    def weightcategoryList(self, agecategory):
        wcl = Weightcategory.objects.filter(agecategory_id=agecategory.id)
        myWcl = ""
        for wc in wcl:
            myWcl = myWcl + wc.weight + " | "
        return myWcl

    weightcategoryList.short_description = "Catégories de poids"
    weightcategoryList.verbose_name_plural = "Catégories de poids"

    fieldsets = (
        # Fieldset 1 : meta-info (titre, auteur…)
        (
            "Général",
            {"fields": ("season", "surname", "name", "gender", ("agemin", "agemax"))},
        ),
        # ('Catégories de poids', {
        #    inlines = [WeightcategoryInline]
        # }),
    )
    inlines = [WeightcategoryInline]

    def response_change(self, request, obj):
        res = super(AgecategoryAdmin, self).response_change(request, obj)
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET["next"])
        else:
            return res


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    max_num = 1
    verbose_name = "Profile"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "ligue",
        "licence",
    )
    list_filter = (
        "profile__region",
        "is_staff",
        "is_superuser",
    )
    inlines = (ProfileInline,)
    list_select_related = ("profile",)

    def licence(self, instance):
        return instance.profile.licence

    def ligue(self, instance):
        return instance.profile.region


class ConcurrentAdmin(admin.ModelAdmin):
    list_display = ("licence", "firstname", "lastname", "date_of_birth")
    # list_filter = ('lastname', 'licence', )
    ordering = ("lastname", "firstname", "licence")
    search_fields = ("lastname", "firstname", "licence", "date_of_birth")


class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "short")
    ordering = ("name",)
    search_fields = ("name", "short")


class WallpaperAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    fields = ("wallpaper",)


class RecordstandardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gender",
        "agecategory",
        "weightcategory",
        "arr",
        "ep_j",
        "total",
    )
    ordering = ("agecategory", "gender", "arr", "ep_j")
    list_filter = (
        "gender",
        "agecategory",
    )


class RecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gender",
        "weightcategory",
        "agecategory",
        "full_name",
        "kind",
        "value",
        "is_current",
    )

    @admin.display(description="Full name")
    def full_name(self, instance):
        full_name = "standard"
        if instance.event:
            full_name = f"{instance.event.concurrent.firstname} {instance.event.concurrent.lastname}"

        return full_name

    @admin.display(description="Genre")
    def gender(self, instance):
        return instance.gender.verbose_name


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "competition__name",
        "eligible",
        "date",
        "full_name",
        "age",
        "attempts",
        "total",
        "closed",
        "season",
    )
    ordering = ("-competition__season",)
    list_filter = (
        "competition__season",
        "competition__isrecordeligible",
        "competition__closed",
        "agecategory__name",
    )
    search_fields = (
        "concurrent__lastname",
        "competition__name",
    )

    @admin.display(description="Full name")
    def full_name(self, instance):
        return f"{instance.concurrent.firstname} {instance.concurrent.lastname}"

    @admin.display(description="Eligible")
    def eligible(self, instance):
        return instance.competition.isrecordeligible

    @admin.display(description="Age")
    def age(self, instance):
        return instance.agecategory.name

    @admin.display(description="Saison")
    def season(self, instance):
        return instance.competition.season

    @admin.display(description="Close")
    def closed(self, instance):
        return instance.competition.closed

    @admin.display(description="Date")
    def date(self, instance):
        return instance.competition.start_date

    @admin.display(description="Attempts")
    def attempts(self, instance):
        attempt_list = list(instance.attempt_set.all())
        result = ""
        arr = ""
        ep_j = ""
        for attempt in attempt_list:
            if attempt.name == "ARR":
                if attempt.validate == 1:
                    arr = arr + "\u0332".join(str(attempt.value)) + " "
                else:
                    arr = arr + str(attempt.value) + " "
            if attempt.name == "EP-J":
                if attempt.validate == 1:
                    ep_j = ep_j + "\u0332".join(str(attempt.value)) + " "
                else:
                    ep_j = ep_j + " " + str(attempt.value) + " "
        result = arr[:-1] + " || " + ep_j[:-1]
        return result


admin.site.register(Agecategory, AgecategoryAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Competitionkind)
admin.site.register(Concurrent, ConcurrentAdmin)
# admin.site.register(Competitionleague)
admin.site.register(Gender)
admin.site.register(Minimumweightcategory, MinimumweightcategoryAdmin)
admin.site.register(Season, SeasonAdmin)
# admin.site.register(Team)
admin.site.register(Weightcategory, WeightcategoryAdmin)
admin.site.register(Leadertype, LeadertypeAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Region, RegionAdmin)
# admin.site.register(Event)
admin.site.register(Wallpaper, WallpaperAdmin)
admin.site.register(RecordStandard, RecordstandardAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Event, EventAdmin)
