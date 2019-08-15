from collections import OrderedDict
from django.contrib import admin
from django.utils.safestring import mark_safe
from politician.models import Party, Politician
from politician.services import PartyService, SenateService, CongressService


class PartiesFilter(admin.SimpleListFilter):
    title = "Parties"
    parameter_name = "party"

    def lookups(self, request, model_admin):
        parties = Party.objects.order_by("initials", "name").all()

        def map_parties(party):
            return (
                party.initials,
                "{}: {}".format(party.initials, party.name),)

        return list(map(map_parties, parties))

    def queryset(self, request, queryset):
        party = request.GET.get("party")
        if party:
            return queryset.filter(party__initials=party)

        return queryset


class PoliticianRoleFilter(admin.SimpleListFilter):
    title = "Role filter"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        return Politician.ROLES

    def queryset(self, request, queryset):
        role = request.GET.get("role")
        if role:
            return queryset.filter(role=request.GET.get("role"))

        return queryset


@admin.register(Politician)
class PoliticianAdmin(admin.ModelAdmin):
    actions = ["load_politicians"]
    list_display = ["get_picture", "name", "role", "party", "updated_at"]
    list_filter = [PoliticianRoleFilter, PartiesFilter]
    search_fields = ["name", "party__initials", "party__name"]

    def get_picture(self, obj):
        if not obj.picture:
            return "-"

        return mark_safe('<img src="{}" width="60" />'.format(obj.picture))

    def load_politicians(self, request, queryset):
        PartyService().load_parties()
        SenateService().load_politicians()
        CongressService().load_politicians()


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    pass
