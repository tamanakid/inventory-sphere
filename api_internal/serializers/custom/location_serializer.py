from rest_framework import serializers

from infra_custom.models import Location
from api_internal.serializers import RecursiveField


class LocationRecursiveSerializer(serializers.ModelSerializer):
	children = RecursiveField(many=True, read_only=True)
	level_is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'level_is_root_storage_level', 'children')


class LocationSerializer(serializers.ModelSerializer):
	level_is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'level_is_root_storage_level', 'parent', 'children')