from rest_framework import serializers

from infra_custom.models import Location, LocationLevel
from api_internal.serializers import RecursiveField, ChoiceField
from api_internal.serializers.custom.location_level_serializers import LocationLevelFlatSerializer


class LocationRecursiveField(serializers.Serializer):
	def to_representation(self, value):
		serializer = (
			LocationFlatSerializer(value, context=self.context)
			if not self.context["all_locations"] and value.level.is_root_storage_level
			else self.parent.parent.__class__(value, context=self.context)
		)
		return serializer.data



class LocationFlatSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		# Would need an instance lookup if provided a non-instance object (i.e. as in the POST method)
		if self.context.get('get_full_path_name', False):
			representation['name'] = instance.get_full_path() 
		return representation

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'is_root_storage_level', 'parent')


class LocationChildrenSerializer(serializers.ModelSerializer):
	children = LocationFlatSerializer(many=True, read_only=True)
	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'is_root_storage_level', 'parent', 'children')


class LocationTreeSerializer(serializers.ModelSerializer):
	children = LocationRecursiveField(many=True, read_only=True)
	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'is_root_storage_level', 'children')




class LocationStructureFlatSerializer(serializers.Serializer):
	child_structure = RecursiveField(many=False, read_only=False, required=False, allow_null=True)
	name = serializers.CharField(required=True)
	index_type = ChoiceField(choices=Location.StructureIndexType, required=True)
	locations_count = serializers.IntegerField(min_value=1, required=True)
	level = LocationLevelFlatSerializer(required=False)


class LocationStructureSerializer(serializers.ModelSerializer):
	child_structure = LocationStructureFlatSerializer(many=False, read_only=False, required=False, allow_null=True)
	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'is_root_storage_level', 'parent', 'child_structure')
