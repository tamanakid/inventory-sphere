from django.contrib import admin

from infra_custom.models import ProductSku


class ProductSkuAttributeValueInline(admin.TabularInline):
    model = ProductSku.attribute_values.through


class ProductSkuAdmin(admin.ModelAdmin):
    inlines = [ProductSkuAttributeValueInline]

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

    list_filter = ['product__client']
    list_display = ('description', 'product')
    ordering = ('description', 'product')

    @admin.display(ordering='product__client')
    def client_name(self, obj):
        return obj.product.client.name


admin.site.register(ProductSku, ProductSkuAdmin)