from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from infra_custom.models import LocationLevel
from api_internal.serializers import LocationLevelSerializer, LocationLevelRecursiveSerializer


# TODO: This permission class is actually quite reusable
class LocationLevelViewPermissions(BasePermission):
	def has_permission(self, request, view):
		return (not request.user.is_anonymous) and (request.user.client is not None)

	def has_object_permission(self, request, view, object):
		return (not request.user.is_anonymous) and (request.user.client is not None) and (request.user.client == object.client)


class LocationLevelViewSet(viewsets.ModelViewSet):
	queryset = LocationLevel.objects.all()
	serializer_class = LocationLevelSerializer
	permission_classes = [LocationLevelViewPermissions]

	''' Internal View Methods '''
	def get_queryset(self, *args, **kwargs):
		root_only = kwargs.get('root_only')

		# TODO: Make sure this is alright
		if self.request.user.is_superuser:
			return LocationLevel.objects.filter(parent=None) if root_only else LocationLevel.objects.all()

		client = self.request.user.client
		return client.location_levels.filter(parent=None) if root_only else client.location_levels.all()


	def get_serializer_class(self):
		return LocationLevelRecursiveSerializer if self.action == 'list' else LocationLevelSerializer


	''' Custom Methods '''


	''' Internal Endpoints '''
	def list(self, request):
		location_levels = self.get_queryset(root_only=True)
		response_content = self.get_serializer(location_levels, many=True).data
		return Response(response_content)
