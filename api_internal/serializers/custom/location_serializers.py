from rest_framework import serializers

from infra_custom.models import Location, LocationLevel
from api_internal.serializers import RecursiveField
from api_internal.serializers.custom.location_level_serializers import LocationLevelFlatSerializer


# class LocationRecursiveSerializer(serializers.ModelSerializer):
# 	children = RecursiveField(many=True, read_only=True)
# 	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

# 	class Meta:
# 		model = Location
# 		fields = ('id', 'name', 'level', 'is_root_storage_level', 'children')


# class LocationSerializer(serializers.ModelSerializer):
# 	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

# 	class Meta:
# 		model = Location
# 		fields = ('id', 'name', 'level', 'is_root_storage_level', 'parent', 'children')


# TODO: This is to become reusable, just as the RecursiveField
class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)



class LocationFlatSerializer(serializers.ModelSerializer):
	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'is_root_storage_level', 'parent')


class LocationChildrenSerializer(serializers.ModelSerializer):
	children = LocationFlatSerializer(many=True, read_only=True)
	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'is_root_storage_level', 'parent', 'children')


class LocationListSerializer(serializers.ModelSerializer):
	children = RecursiveField(many=True, read_only=True)
	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'is_root_storage_level', 'children')




class LocationStructureFlatSerializer(serializers.Serializer):
	child_structure = RecursiveField(many=False, read_only=False, required=False, allow_null=True)
	name = serializers.CharField(required=True)
	index = ChoiceField(choices=Location.StuctureIndex, required=True)
	locations_count = serializers.IntegerField(min_value=1, required=True)
	level = LocationLevelFlatSerializer(required=False)


class LocationStructureSerializer(serializers.ModelSerializer):
	child_structure = LocationStructureFlatSerializer(many=False, read_only=False, required=False, allow_null=True)
	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

	class Meta:
		model = Location
		fields = ('id', 'name', 'level', 'is_root_storage_level', 'parent', 'child_structure')
