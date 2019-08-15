from collections import OrderedDict
from django.contrib import admin
from django.utils.safestring import mark_safe
from politician.models import Party, Politician
from politician.services import PartyService, SenateService


@admin.register(Politician)
class PoliticianAdmin(admin.ModelAdmin):
    actions = ["load_politicians"]
    list_display = ["get_picture", "name", "role", "party", "updated_at"]
    search_fields = ["name", "party__initials", "party__name"]

    def get_picture(self, obj):
        if not obj.picture:
            return "-"

        return mark_safe('<img src="{}" width="60" />'.format(obj.picture))

    def load_politicians(self, request, queryset):
        PartyService().load_parties()
        SenateService().load_politicians()


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    pass
