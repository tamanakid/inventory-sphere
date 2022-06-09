
from rest_framework import serializers


class APIPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.client_field = kwargs.pop('client_field', 'client')
        super().__init__(**kwargs)
    
    def get_queryset(self):
        kwargs = { self.client_field: self.context.get('client') }
        queryset = super().get_queryset().filter(**kwargs)
        return queryset


'''
The following Field is used by certain model serializers to filter their related objects by client

i.e If a POST request for Categories is only supposed to pass its related Attributes' IDs (instead of the full object)
    The field is added to the Serializer, which will provide the matching related objects (Attributes) to the serializer methods (i.e create())

class CategoryFlatSerializer(BaseAPIModelSerializer):
    ...
    attribute_ids = APIPrimaryKeyRelatedField(queryset=Attribute.objects.all(), write_only=True, many=True)
	...
    def create(self, validated_data):
        attributes = validated_data.pop('attribute_ids')
        category = Category.objects.create(**validated_data)
        for attribute in attributes:
            category.attributes.add(attribute)
        return category
'''
