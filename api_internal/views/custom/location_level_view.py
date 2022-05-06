from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from api_internal.views import BaseView #BaseAPIView

from infra_custom.models import LocationLevel
from api_internal.serializers import LocationLevelFlatSerializer, LocationLevelChildrenSerializer, LocationLevelCreateSerializer, LocationLevelListSerializer


# TODO: This permission class is actually quite reusable along the application
class LocationLevelViewPermissions(BasePermission):
	def has_permission(self, request, view):
		return (not request.user.is_anonymous) and (request.user.client is not None)

	def has_object_permission(self, request, view, object):
		return (not request.user.is_anonymous) and (request.user.client is not None) and (request.user.client == object.client)


class LocationLevelBaseView(BaseView):
	permission_classes = [LocationLevelViewPermissions]

	def get_queryset(self, *args, **kwargs):
		root_only = kwargs.get('root_only')
		
		if self.request.user.is_superuser:
			return LocationLevel.objects.filter(parent=None) if root_only else LocationLevel.objects.all()

		client = self.request.user.client
		return client.location_levels.filter(parent=None) if root_only else client.location_levels.all()


class LocationLevelsListView(LocationLevelBaseView):
	def get_serializer_class(self):
		if self.request.method == 'POST':
			return LocationLevelFlatSerializer
		return LocationLevelListSerializer

	def get(self, request):
		location_levels = self.get_queryset(root_only=True)
		# Test how to paginate tree lists
		serializer = self.get_serializer(location_levels, many=True)
		return Response(serializer.data)
	
	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class LocationLevelViewSet(BaseView):

	# def get_serializer_class(self):
	# 	if self.action == 'retrieve':
	# 		return LocationLevelChildrenSerializer
	# 	if self.action == 'destroy':
	# 		return LocationLevelFlatSerializer
	# 	if self.action == 'list':
	# 		return LocationLevelListSerializer
	# 	if self.action == 'create':
	# 		return LocationLevelCreateSerializer
	# 	return LocationLevelListSerializer

	''' Custom Methods '''


	# ''' Internal Endpoints '''
	# def get(self, request):
	# 	queryset = self.get_queryset(root_only=True)
	# 	# No need for pagination in tree lists?
	# 	serializer = self.get_serializer(queryset, many=True)
	# 	return Response(serializer.data)

	'''The following may work for Locations POST requests'''
	# def create(self, request, *args, **kwargs):
	# 	root_object = request.data
	# 	self.create_recursive(root_object, parent_id=root_object.get('parent'))
	# 	return Response(None, status=status.HTTP_201_CREATED)
	
	# def create_recursive(self, obj, *args, **kwargs):
	# 	parent = LocationLevel.objects.get(pk=kwargs.get('parent_id')) if kwargs.get('parent_id') is not None else None
	# 	instance = LocationLevel.objects.create(
	# 		client=self.request.user.client,
	# 		parent=parent,
	# 		name=obj.get('name'),
	# 		is_root_storage_level=obj.get('is_root_storage_level')
	# 	)
	# 	instance.save()

	# 	children = obj.get('children')
	# 	instance_id = instance.id if (instance.id is not None) else 100
	# 	for child in children:
	# 		self.create_recursive(child, parent_id=instance_id)
		

	
	# def perform_create(self, serializer):
	# 	serializer.save(client=self.request.user.client)
	# 	return serializer
