from django.utils.functional import cached_property
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from infra_auth.models import User
from .base_api_permission import BaseAPIPermission


write_methods = ['POST', 'PUT', 'DELETE']


class InventoryManagerWriteElseReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        # has_base_perm = super().has_permission(request, view)
        is_write_method = request.method in write_methods
        is_inventory_manager = request.user.role == User.Role.INVENTORY_MANAGER

        # return has_base_perm and (is_inventory_manager or not is_write_method)
        return is_inventory_manager or not is_write_method
    
    def has_object_permission(self, request, view, object):
        # has_base_perm = super().has_permission(request, view)
        is_write_method = request.method in write_methods
        is_inventory_manager = request.user.role == User.Role.INVENTORY_MANAGER

        # return has_base_perm and (is_inventory_manager or not is_write_method)
        return is_inventory_manager or not is_write_method
