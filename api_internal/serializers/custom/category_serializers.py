from collections import OrderedDict
from rest_framework import serializers

from infra_custom.models import Category, Attribute
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
                ('is_attribute_required', attribute.categories.through.objects.get(attribute=attribute, category=category).is_attribute_required),
            ])
            representation.append(attr_dict)
        return representation


class CategoryFlatSerializer(CategoryBaseSerializer):
    id = serializers.IntegerField(required=False)
    attributes = AttributeSerializer(many=True, read_only=True)
    attribute_ids_required = APIPrimaryKeyRelatedField(queryset=Attribute.objects.all(), write_only=True, many=True)
    attribute_ids_not_required = APIPrimaryKeyRelatedField(queryset=Attribute.objects.all(), write_only=True, many=True)
	
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'attributes', 'attribute_ids_required', 'attribute_ids_not_required')
    
    def _set_attributes_required_flag(self, category, attributes_required, attributes_not_required):
        category_attributes = category.attributes.through.objects.filter(category=category)
        for category_attribute in category_attributes:
            if category_attribute.attribute in attributes_required:
                category_attribute.is_attribute_required = True
                category_attribute.save()
            elif category_attribute.attribute in attributes_not_required:
                category_attribute.is_attribute_required = False
                category_attribute.save()
    
    def update(self, instance, validated_data):
        super().update(instance, validated_data)

        # Maps for instance's current attributes and request's new attributes.
        current_attrs = { attr.id: attr for attr in instance.attributes.all() }
        new_attrs_required = { attr.id: attr for attr in validated_data.pop('attribute_ids_required') }
        new_attrs_not_required = { attr.id: attr for attr in validated_data.pop('attribute_ids_not_required') }

        # Perform deletions.
        for attr_id, attr in current_attrs.items():
            instance.attributes.remove(attr)
        
        # Perform re-creations
        for attribute in new_attrs_required:
            instance.attributes.add(attribute)
        for attribute in new_attrs_not_required:
            instance.attributes.add(attribute)

        self._set_attributes_required_flag(instance, list(new_attrs_required.values()), list(new_attrs_not_required.values()))
        
        return instance

    def create(self, validated_data):
        attributes_required = validated_data.pop('attribute_ids_required')
        attributes_not_required = validated_data.pop('attribute_ids_not_required')

        category = Category.objects.create(**validated_data)

        for attribute in attributes_required + attributes_not_required:
            category.attributes.add(attribute)
        
        self._set_attributes_required_flag(category, attributes_required, attributes_not_required)
        
        return category


class CategoryDetailsSerializer(CategoryBaseSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)

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


class CategoryForeignSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['full_path_name'] = instance.get_full_path()
        return representation

    class Meta:
        model = Category
        fields = ('id', 'name')