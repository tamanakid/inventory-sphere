from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from api_internal.views import BaseView
from api_internal.permissions import BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission
from api_internal.serializers import LocationLevelFlatSerializer, LocationLevelChildrenSerializer, LocationLevelTreeSerializer

from infra_custom.models import LocationLevel


class LocationLevelsBaseView(BaseView):
	permission_classes = (BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		root_only = kwargs.get('root_only')
				
		query = LocationLevel.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(client=self.client)
			
		if root_only:
			query = query.filter(parent=None)
		
		return query



class LocationLevelsListView(LocationLevelsBaseView):
	
	def get_serializer_class(self):
		if self.request.method == 'POST':
			return LocationLevelFlatSerializer
		return LocationLevelFlatSerializer

	def get(self, request):
		location_levels = self.paginator.paginate_queryset(self.get_queryset(), request)
		# Test how to paginate tree lists
		serializer = self.get_serializer(location_levels, many=True, context={'get_full_path_name': True})
		return self.paginator.get_paginated_response(serializer.data)
	
	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)



class LocationLevelsTreeView(LocationLevelsBaseView):
    def get_serializer_class(self):
        return LocationLevelTreeSerializer
    
    def get(self, request):
        location_levels = self.get_queryset(root_only=True)
		# Test how to paginate tree lists
        serializer = self.get_serializer(location_levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class LocationLevelView(LocationLevelsBaseView):
	lookup_url_kwarg = 'id'

	def get_serializer_class(self):
		return LocationLevelChildrenSerializer

	def get(self, request, id):
		location_level = self.get_object()
		serializer = self.get_serializer(location_level)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def put(self, request, id):
		location_level = self.get_object()
		serializer = self.get_serializer(location_level, data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

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


class LocationLevelsDeleteView(LocationLevelsBaseView):
	def post(self, request):
		ids_to_delete = request.data.get('ids', None)
		location_levels = self.get_queryset().filter(id__in=ids_to_delete)
		for location_level in location_levels:
			location_levels.delete()
		return Response(status=status.HTTP_200_OK)