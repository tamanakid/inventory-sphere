from collections import OrderedDict
from logging import Filter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from django.core.exceptions import ValidationError
# TODO: Prolly better to use and handle the DRF ValidationError
# from rest_framework import exceptions

from api_internal.views import BaseView
from api_internal.permissions import BaseAPIPermission, ManagerRolesWriteElseReadOnlyPermission
from api_internal.serializers import LocationFlatSerializer, LocationListSerializer, LocationChildrenSerializer, LocationStructureSerializer, LocationStructureFlatSerializer

from infra_custom.models import Location, LocationLevel



class LocationsBaseView(BaseView):
	permission_classes = (BaseAPIPermission, ManagerRolesWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		root_only = kwargs.get('root_only')
		
		query = Location.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(level__client=self.client)
			
		if root_only:
			query = query.filter(parent=None)
		
		return query



class LocationsListView(LocationsBaseView):
	
	def get_serializer_class(self):
		if self.request.method == 'POST':
			return LocationStructureSerializer
		return LocationListSerializer

	def get(self, request):
		all_locations = request.query_params.get('all_locations', '').lower() == 'true'
		locations = self.get_queryset(root_only=True)
		# Test how to paginate tree lists
		serializer = self.get_serializer(locations, many=True, context={'all_locations': all_locations})
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def post(self, request):
		created_locations = self._create_location_from_structure(request.data, self.get_serializer_class())
		serializer = LocationFlatSerializer(data=created_locations, many=True)
		serializer.is_valid()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	

	def _create_location_from_structure(self, raw_data, serializer_class):
		created_instances = []

		serializer = serializer_class(data=raw_data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data

		instance = Location.objects.create(
			name=data.get('name'),
			level=data.get('level'),
			parent=data.get('parent'),
		)
		instance.save()

		created_instances.append({ 'name': instance.name, 'parent': instance.parent.id, 'level': instance.level.id, 'id': instance.id })

		child_structure = raw_data.get('child_structure', None)
		if child_structure is not None:
			# Make sure either there's only one child level, or a specific child level is specified
			child_explicit_level = child_structure.get('level')
			child_levels = data.get('level').get_direct_descendants()
			if child_explicit_level is None and child_levels.count() > 1:
				# raise exceptions.ValidationError(details=)
				raise ValidationError(f'The parent LocationLevel must be of the same client')
			
			child_level = child_levels.first() if child_levels.count() == 1 else LocationLevel.objects.get(id=child_explicit_level)

			for i in range(child_structure.get('locations_count')):
				name = child_structure.get('name')
				child_data = OrderedDict([
					('name', f'{name} ({i})'),
					('level', child_level.id),
					('parent', instance.id),
					('child_structure', child_structure.get('child_structure'))
				])
				created_children = self._create_location_from_structure(child_data, LocationStructureSerializer)
				created_instances.extend(created_children)
		
		return created_instances



class LocationsView(LocationsBaseView):
	lookup_url_kwarg = 'id'

	def get_serializer_class(self):
		return LocationChildrenSerializer

	def get(self, request, id):
		location = self.get_object()
		serializer = self.get_serializer(location)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def put(self, request, id):
		location = self.get_object()
		serializer = self.get_serializer(location, data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def delete(self, request, id):
		location = self.get_object()
		location.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)