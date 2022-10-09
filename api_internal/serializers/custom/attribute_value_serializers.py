from rest_framework import serializers

from infra_custom.models import Attribute, AttributeValue
from api_internal.serializers import RecursiveField, ChoiceField
from api_internal.serializers.custom.location_level_serializers import LocationLevelFlatSerializer
from django.core.exceptions import ValidationError



class AttributeValueGetSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)

	class Meta:
		model = AttributeValue
		fields = ('id', 'name', 'abbreviation')


class AttributeValueSaveSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)

	def update(self, attribute_value_instance, validated_data):
		new_attribute = validated_data.get('attribute')
		new_abbreviation = validated_data.get('abbreviation')
		if new_attribute.is_value_abbrev_required and new_abbreviation == None:
			raise ValidationError(f'Values for Attribute "{new_attribute.name}" must have an Abbreviation', None, { 'field': 'abbreviation' })
		
		super().update(attribute_value_instance, validated_data)
		return attribute_value_instance

	class Meta:
		model = AttributeValue
		fields = ('id', 'attribute', 'name', 'abbreviation')