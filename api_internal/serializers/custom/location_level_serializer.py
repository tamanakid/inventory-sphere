from rest_framework import serializers

from infra_custom.models import LocationLevel
from api_internal.serializers import RecursiveField


class LocationLevelRecursiveSerializer(serializers.ModelSerializer):
	children = RecursiveField(many=True, read_only=True)

	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'children')


class LocationLevelSerializer(serializers.ModelSerializer):
	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'children')