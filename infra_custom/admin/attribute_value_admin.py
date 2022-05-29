from django.contrib import admin

from infra_custom.models import AttributeValue


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    fields = ('name', 'attribute', 'abbreviation')


class AttributeValueAdmin(admin.ModelAdmin):
    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('attribute', 'name', 'abbreviation'),
        }),
    )
    # For edition
    fieldsets = (
        (None, { 'fields': ['attribute', 'name', 'abbreviation'] }),
    )

    raw_id_fields = ['attribute']
    list_filter = ['attribute__client', 'attribute']
    list_display = ('name_verbose', 'attribute', 'client_name', 'abbreviation')
    ordering = ('attribute', 'name')

    @admin.display(ordering='attribute__client')
    def client_name(self, obj):
        return obj.attribute.client.name

    @admin.display()
    def name_verbose(self, obj):
        return f"{obj.name} ({obj.attribute.name})"


admin.site.register(AttributeValue, AttributeValueAdmin)