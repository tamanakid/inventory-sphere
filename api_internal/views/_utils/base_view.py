from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission


class BaseViewPermissions(BasePermission):
	def has_permission(self, request, view):
		return (not request.user.is_anonymous) and (request.user.client is not None)

	def has_object_permission(self, request, view, object):
		return (not request.user.is_anonymous) and (request.user.client is not None) and (request.user.client == object.client)


class BaseView(GenericAPIView):
    permission_classes = [BaseViewPermissions]

    @property
    def client(self):
        return self.request.user.client if (not self.request.user.is_anonymous) else None

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'client': self.client
        }
