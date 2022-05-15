from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from infra_custom.models import Location
from api_internal.serializers import LocationSerializer, LocationRecursiveSerializer


# TODO: This permission class is actually quite reusable
class LocationViewPermissions(BasePermission):
	def has_permission(self, request, view):
		return (not request.user.is_anonymous) and (request.user.client is not None)

	def has_object_permission(self, request, view, object):
		return (not request.user.is_anonymous) and (request.user.client is not None) and (request.user.client == object.client)


class LocationViewSet(viewsets.ModelViewSet):
	queryset = Location.objects.all()
	serializer_class = LocationSerializer
	permission_classes = [LocationViewPermissions]

	''' Internal View Methods '''
	def get_queryset(self, *args, **kwargs):
		root_only = kwargs.get('root_only')

		# TODO: Make sure this is alright
		if self.request.user.is_superuser:
			return Location.objects.filter(parent=None) if root_only else Location.objects.all()

		client = self.request.user.client
		return Location.objects.filter(parent=None, level__client=client) if root_only else Location.objects.filter(level__client=client)


	def get_serializer_class(self):
		return LocationRecursiveSerializer if self.action == 'list' else LocationSerializer


	''' Custom Methods '''


	''' Internal Endpoints '''
	def list(self, request):
		locations = self.get_queryset(root_only=True)
		response_content = self.get_serializer(locations, many=True).data
		return Response(response_content)
