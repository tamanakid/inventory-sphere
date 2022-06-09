from wsgiref import validate
from collections import OrderedDict
from rest_framework import serializers

from infra_custom.models import Category, Attribute, CategoryAttribute
from api_internal.serializers import RecursiveField, BaseAPIModelSerializer, APIPrimaryKeyRelatedField
from api_internal.serializers.custom.attribute_serializers import AttributeSerializer


class CategoryBaseSerializer(BaseAPIModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['attributes'] = self._get_category_attributes_to_representation(instance)
        return representation

    def _get_category_attributes_to_representation(self, category):
        representation = []
        for attribute in category.attributes.all():
            attr_dict = OrderedDict([
                ('id', attribute.id),
                ('name', attribute.name),
                ('is_attribute_required', attribute.category_set.through.objects.get(attribute=attribute, category=category).is_attribute_required),
                # attribute.categoryattribute_set.get(category=category).is_attribute_required
            ])
            representation.append(attr_dict)
        return representation


class CategoryFlatSerializer(CategoryBaseSerializer):
    id = serializers.IntegerField(required=False)
    attributes = AttributeSerializer(many=True, read_only=True)
    attribute_ids = APIPrimaryKeyRelatedField(queryset=Attribute.objects.all(), write_only=True, many=True)
	
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'attributes', 'attribute_ids')
    
    def update(self, instance, validated_data):
        super().update(instance, validated_data)

        # Maps for instance's current attributes and request's new attributes.
        current_attrs = { attr.id: attr for attr in instance.attributes.all() }
        new_attrs = { attr.id: attr for attr in validated_data.pop('attribute_ids') }

        # # Perform creations and updates.
        for new_attr_id, new_attr in new_attrs.items():
            attr = current_attrs.get(new_attr_id, None)
            if attr is None:
                instance.attributes.add(new_attr)

        # # Perform deletions.
        for attr_id, attr in current_attrs.items():
            if attr_id not in new_attrs:
                instance.attributes.remove(attr)
        
        return instance

    def create(self, validated_data):
        attributes = validated_data.pop('attribute_ids')
        category = Category.objects.create(**validated_data)
        for attribute in attributes:
            category.attributes.add(attribute)
        return category


class CategoryDetailsSerializer(CategoryBaseSerializer):
	class Meta:
		model = Category
		fields = ('id', 'name', 'parent', 'attributes')


class CategoryListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ('id', 'name', 'parent')


class CategoryTreeSerializer(serializers.ModelSerializer):
	children = RecursiveField(many=True, read_only=True)

	class Meta:
		model = Category
		fields = ('id', 'name', 'children')
