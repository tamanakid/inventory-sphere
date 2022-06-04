from django.contrib import admin
from django.db.models import F
from django import forms

from infra_custom.models import Attribute, Category


def category_form_factory(obj):
    class CategoryForm(forms.ModelForm):        
        parent = forms.ModelChoiceField(
            queryset=Category.objects.filter(client=obj.client),
            required=False
        )
    return CategoryForm


class CategoryAttributeInline(admin.TabularInline):
    model = Category.attributes.through


class CategoryAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj is not None and obj.client is not None:
            kwargs['form'] = category_form_factory(obj)
        return super(CategoryAdmin, self).get_form(request, obj, **kwargs)
    
    filter_horizontal = ('attributes', )

    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('client', 'name', 'parent'),
        }),
    )
    # For edition
    fieldsets = (
        ('Client', {'fields': ['client']}),
        (None, { 'fields': ['name', 'parent'] }),
    )

    raw_id_fields = ['client', 'parent']

    list_filter = ['client']
    list_display = ('name', 'client', 'parent')
    ordering = ('client', F('parent').asc(nulls_first=True), 'name')

    inlines = [CategoryAttributeInline]


admin.site.register(Category, CategoryAdmin)