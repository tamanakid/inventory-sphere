from django.contrib import admin
from django.db.models import F
from django import forms

from infra_custom.models import Product


def product_form_factory(obj):
    class ProductForm(forms.ModelForm):        
        parent = forms.ModelChoiceField(
            queryset=Product.objects.filter(client=obj.client),
            required=False
        )
    return ProductForm


class ProductAttributeInline(admin.TabularInline):
    model = Product.attributes.through


class ProductAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj is not None and obj.client is not None:
            kwargs['form'] = product_form_factory(obj)
        return super(ProductAdmin, self).get_form(request, obj, **kwargs)
    
    filter_horizontal = ('attributes', )

    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('client', 'category', 'name', 'brand'),
        }),
    )
    # For edition
    fieldsets = (
        ('Client', {'fields': ['client']}),
        (None, { 'fields': ['category', 'name', 'brand'] }),
        ('Current Attributes', { 'fields': ['attributes_qs'] })
    )

    raw_id_fields = ['client', 'category']

    list_filter = ['client']
    list_display = ('name', 'client', 'category')
    ordering = ('client', 'category', 'name')

    readonly_fields = ['attributes_qs']

    inlines = [ProductAttributeInline]


admin.site.register(Product, ProductAdmin)