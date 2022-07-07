from django.contrib import admin
from django.db.models import F
from django import forms

from infra_custom.models import Product, ProductSku
from infra_custom.signals import add_attribute_value_to_product_sku


class ProductSkuAttributeValueInline(admin.TabularInline):
    model = ProductSku.attribute_values.through


class ProductSkuAdmin(admin.ModelAdmin):    
    # filter_horizontal = ('attribute_values', )
    inlines = [ProductSkuAttributeValueInline]

    # def save_related(self, request, form, formsets, change):
    #     add_attribute_value_to_product_sku(ProductSku.attribute_values.through, instance=form.instance)

    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('product', 'description', 'is_valid'),
        }),
    )
    # For edition
    fieldsets = (
        (None, { 'fields': ['product', 'description', 'is_valid'] }),
    )

    # raw_id_fields = ['client', 'category']
    # readonly_fields = ['is_valid']

    list_filter = ['product__client']
    list_display = ('description', 'product')
    ordering = ('description', 'product')

    @admin.display(ordering='product__client')
    def client_name(self, obj):
        return obj.product.client.name

    # inlines = [ProductAttributeInline]


admin.site.register(ProductSku, ProductSkuAdmin)