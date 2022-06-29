from django.contrib import admin
from django.db.models import F
from django import forms

from infra_custom.models import Product, ProductSku


class ProductSkuAttributeValueInline(admin.TabularInline):
    model = ProductSku.attribute_values.through


class ProductSkuAdmin(admin.ModelAdmin):    
    # filter_horizontal = ('attribute_values', )
    inlines = [ProductSkuAttributeValueInline]

    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('product', 'description'),
        }),
    )
    # For edition
    fieldsets = (
        (None, { 'fields': ['product', 'description'] }),
    )

    # raw_id_fields = ['client', 'category']

    # list_filter = ['client']
    # list_display = ('name', 'client', 'category')
    # ordering = ('client', 'category', 'name')

    # inlines = [ProductAttributeInline]


admin.site.register(ProductSku, ProductSkuAdmin)