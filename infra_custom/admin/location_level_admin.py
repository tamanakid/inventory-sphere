from django.contrib import admin
from django.db.models import F
from django import forms

from infra_custom.models import LocationLevel
from .location_admin import LocationInline


def location_level_form_factory(client):
    class LocationLevelForm(forms.ModelForm):
        parent = forms.ModelChoiceField(
            queryset=LocationLevel.objects.filter(client=client),
        )
    return LocationLevelForm


class LocationLevelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj is not None and obj.client is not None:
            kwargs['form'] = location_level_form_factory(obj.client)
        return super(LocationLevelAdmin, self).get_form(request, obj, **kwargs)

    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('client', 'name', 'parent', 'is_root_storage_level'),
        }),
    )
    # For edition
    fieldsets = (
        ('Client', {'fields': ['client']}),
        (None, { 'fields': ['name'] }),
        ('Location Level Config', {'fields': ('is_root_storage_level', 'parent')})
    )

    raw_id_fields = ['client', 'parent']
    # autocomplete_fields = ['client', 'parent']
    # search_fields = ['client']

    list_filter = ['client']
    list_display = ('name', 'client', 'parent', 'is_root_storage_level')
    ordering = ('client', F('parent').asc(nulls_first=True), 'name')

    inlines = [LocationInline]


admin.site.register(LocationLevel, LocationLevelAdmin)