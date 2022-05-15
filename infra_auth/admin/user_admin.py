from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from infra_auth.models import User


class UserInline(admin.TabularInline):
    model = User
    fields = ('email', 'user_permissions', 'groups', 'is_active')


class UserAdmin(DefaultUserAdmin):
    # For creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'client', 'role', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    # For edition
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    list_filter = ['client', 'is_superuser', 'role']
    list_display = ('email', 'client_name', 'role', 'first_name', 'last_name')
    ordering = ['client', 'role']

    @admin.display(ordering='client__name')
    def client_name(self, obj):
        return obj.client.name if obj.client is not None else '-'



admin.site.register(User, UserAdmin)