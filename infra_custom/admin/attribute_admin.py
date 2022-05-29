from django.contrib import admin

from infra_custom.models import Attribute
from .attribute_value_admin import AttributeValueInline



class AttributeAdmin(admin.ModelAdmin):
    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('client', 'name', 'is_value_abbrev_required'),
        }),
    )
    # For edition
    fieldsets = (
        ('Client', {'fields': ['client']}),
        (None, { 'fields': ['name', 'is_value_abbrev_required'] }),
    )

    raw_id_fields = ['client']

    list_filter = ['client']
    list_display = ('name', 'client')
    ordering = ('client', 'name')

    inlines = [AttributeValueInline]


admin.site.register(Attribute, AttributeAdmin)