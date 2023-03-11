from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from api_internal.views import BaseView, BaseDeleteView
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


class LocationLevelsDeleteView(BaseDeleteView, LocationLevelsBaseView):
	pass