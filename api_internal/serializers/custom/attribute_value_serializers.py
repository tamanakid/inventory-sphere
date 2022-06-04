from rest_framework import serializers

from infra_custom.models import Attribute, AttributeValue
from api_internal.serializers import RecursiveField, ChoiceField
from api_internal.serializers.custom.location_level_serializers import LocationLevelFlatSerializer



class AttributeValueGetSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)

	class Meta:
		model = AttributeValue
		fields = ('id', 'name', 'abbreviation')


class AttributeValueSaveSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)

	class Meta:
		model = AttributeValue
		fields = ('id', 'attribute', 'name', 'abbreviation')