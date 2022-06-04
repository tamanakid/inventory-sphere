from rest_framework import serializers

from infra_custom.models import Attribute, AttributeValue
from api_internal.serializers import BaseAPIModelSerializer
from api_internal.serializers.custom.attribute_value_serializers import AttributeValueGetSerializer



class AttributeSerializer(BaseAPIModelSerializer):
	id = serializers.IntegerField(required=False)

	class Meta:
		model = Attribute
		fields = ('id', 'name', 'is_value_abbrev_required')


class AttributeWithValuesListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    attribute_values = AttributeValueGetSerializer(many=True)
    
    class Meta:
        model = Attribute
        fields = ('id', 'name', 'is_value_abbrev_required', 'attribute_values')