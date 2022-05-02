from rest_framework import serializers

from infra_custom.models import LocationLevel
from api_internal.serializers import RecursiveField


class LocationLevelFlatSerializer(serializers.ModelSerializer):
	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'parent')


class LocationLevelChildrenSerializer(serializers.ModelSerializer):
	children = LocationLevelFlatSerializer(many=True, read_only=True)

	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'parent', 'children')


class LocationLevelListSerializer(serializers.ModelSerializer):
	children = RecursiveField(many=True, read_only=True)

	class Meta:
		model = LocationLevel
		fields = ('id', 'name', 'is_root_storage_level', 'children')


class LocationLevelCreateSerializer(serializers.ModelSerializer):
	children = RecursiveField(many=True)

	class Meta:
		model = LocationLevel
		fields = ('name', 'is_root_storage_level', 'children', 'parent')
	
	# def create(self, validated_data):
	# 	self.create_children()
	# 	return location_level
	
	# @staticmethod
	# # https://gist.github.com/abirafdirp/c11ee2d7788f3643f29f503b4f548cdd
	# def create_children():
	# 	pass