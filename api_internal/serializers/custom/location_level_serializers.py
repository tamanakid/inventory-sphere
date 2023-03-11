from rest_framework import serializers

from infra_custom.models import LocationLevel
from api_internal.serializers import RecursiveField, BaseAPIModelSerializer


class LocationLevelFlatSerializer(BaseAPIModelSerializer):
	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'parent')
	
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		# Would need an instance lookup if provided a non-instance object (i.e. as in the POST method)
		if self.context.get('get_full_path_name', False):
			representation['name'] = instance.get_full_path() 
		return representation


class LocationLevelChildrenSerializer(serializers.ModelSerializer):
	children = LocationLevelFlatSerializer(many=True, read_only=True)

	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'parent', 'children')


class LocationLevelTreeSerializer(BaseAPIModelSerializer):
	children = RecursiveField(many=True, read_only=True)

	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'children')
