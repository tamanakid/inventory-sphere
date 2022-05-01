from django.contrib import admin

from infra_auth.models import Client
from infra_auth.admin.user_admin import UserInline


# @admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    def __str__(self):
        return self.name

    '''
    fields = ('name', 'employees')
    readonly_fields = ['employees']

    @admin.display()
    def employees(self, client):
        return client.employees
    '''
    inlines = [UserInline]
    ordering = ['name']
    # search_fields = ['name']


admin.site.register(Client, ClientAdmin)
