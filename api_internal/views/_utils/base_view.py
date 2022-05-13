from django.utils.functional import cached_property
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from infra_auth.models import Client


class BaseViewPermissions(BasePermission):
	def has_permission(self, request, view):
		return (not request.user.is_anonymous) and (view.client is not None)

	def has_object_permission(self, request, view, object):
		return (not request.user.is_anonymous) and (view.client is not None) and (view.client == object.client)


class BaseView(GenericAPIView):
    permission_classes = [BaseViewPermissions]
    authentication_classes = [JWTTokenUserAuthentication]

    @cached_property
    def client(self):
        return Client.objects.get(id=self.request.user.client_id)

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'client': self.client
        }
