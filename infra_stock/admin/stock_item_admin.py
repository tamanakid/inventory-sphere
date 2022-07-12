from django.contrib import admin

from infra_stock.models.stock_item import StockItem


class StockItemAdmin(admin.ModelAdmin):
    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('sku', 'location'),
        }),
    )
    # For edition
    fieldsets = (
        (None, { 'fields': ['sku', 'location'] }),
    )

    raw_id_fields = ['sku', 'location']

    list_filter = ['sku__product__client']
    list_display = ('id', 'sku', 'location')
    ordering = ('sku', 'location')


admin.site.register(StockItem, StockItemAdmin)