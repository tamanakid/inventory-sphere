from django.contrib import admin

from infra_custom.models import Location


class LocationInline(admin.TabularInline):
    model = Location
    fields = ('name', 'parent', 'level')


class LocationAdmin(admin.ModelAdmin):
    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('client_name', 'name', 'parent', 'level'),
        }),
    )
    # For edition
    fieldsets = (
        (None, { 'fields': ['name'] }),
        ('Location Config', {'fields': ('parent', 'level')}),
    )

    raw_id_fields = ['parent', 'level']
    list_filter = ['level__client']
    list_display = ('name', 'client_name', 'level', 'parent', 'is_root_storage_level')
    ordering = ('level', 'parent', 'name')

    @admin.display(ordering='level__client')
    def client_name(self, obj):
        return obj.level.client.name

    @admin.display()
    def is_root_storage_level(self, obj):
        return obj.level.is_root_storage_level


admin.site.register(Location, LocationAdmin)