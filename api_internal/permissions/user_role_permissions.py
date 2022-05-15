from django.utils.functional import cached_property
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from infra_auth.models import User
from .base_api_permission import BaseAPIPermission


write_methods = ['POST', 'PUT', 'DELETE']

manager_roles = [User.Role.INVENTORY_MANAGER, User.Role.STORAGE_MANAGER]
storage_roles = [User.Role.INVENTORY_MANAGER, User.Role.STORAGE_MANAGER, User.Role.STORAGE_EMPLOYEE]
data_roles = [User.Role.INVENTORY_MANAGER, User.Role.DATA_EMPLOYEE]


class InventoryManagerPermission(BasePermission):
    def has_permission(self, request, view):
        is_inventory_manager = request.user.role == User.Role.INVENTORY_MANAGER

        return is_inventory_manager


# For most customization features (i.e. Categorization, Product, etc.)
class InventoryManagerWriteElseReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        is_write_method = request.method in write_methods
        is_inventory_manager = request.user.role == User.Role.INVENTORY_MANAGER

        return is_inventory_manager or not is_write_method


# i.e. View List of Users
class ManagerRolesPermission(BasePermission):
    def has_permission(self, request, view):
        is_manager = request.user.role in manager_roles

        return is_manager


# i.e. Approval of some Storage Operations
class ManagerRolesWriteElseReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        is_write_method = request.method in write_methods
        is_manager = request.user.role in manager_roles

        return is_manager or not is_write_method


# All other storage operations
class StorageRolesWriteElseReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        is_write_method = request.method in write_methods
        is_storage_role = request.user.role in storage_roles

        return is_storage_role or not is_write_method


# Future Data-related operations (i.e., Reports)
class DataRolesPermissions(BasePermission):
    def has_permission(self, request, view):
        is_write_method = request.method in write_methods
        is_storage_role = request.user.role in storage_roles

        return is_storage_role or not is_write_method