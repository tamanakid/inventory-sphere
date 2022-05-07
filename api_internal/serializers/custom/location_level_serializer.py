from rest_framework import serializers

from infra_custom.models import LocationLevel
from api_internal.serializers import RecursiveField, BaseAPISerializer, BaseAPIModelSerializer


class LocationLevelFlatSerializer(BaseAPIModelSerializer):
	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'parent')
	
	# May be redundant
	def create(self, validated_data):
		return super().create(validated_data)


class LocationLevelChildrenSerializer(serializers.ModelSerializer):
	children = LocationLevelFlatSerializer(many=True, read_only=True)

	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'parent', 'children')


class LocationLevelListSerializer(BaseAPIModelSerializer):
	children = RecursiveField(many=True, read_only=True)

	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'children')
