from rest_framework.permissions import BasePermission


class BaseAPIPermission(BasePermission):
	def has_permission(self, request, view):
		return (not request.user.is_anonymous) and (view.client is not None)

	def has_object_permission(self, request, view, object):
		return (not request.user.is_anonymous) and (view.client is not None) and (view.client == object.client)