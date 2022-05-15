from django.utils.functional import cached_property
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from infra_auth.models import Client
from api_internal.permissions import BaseAPIPermission


class BaseView(GenericAPIView):
    permission_classes = [BaseAPIPermission]
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
