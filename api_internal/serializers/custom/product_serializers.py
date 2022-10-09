from collections import OrderedDict
from rest_framework import serializers
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from infra_custom.models import Product, Attribute, Category
from api_internal.serializers import BaseAPIModelSerializer, APIPrimaryKeyRelatedField
from api_internal.serializers.custom.category_serializers import CategoryForeignSerializer



class ProductSerializer(BaseAPIModelSerializer):
	id = serializers.IntegerField(required=False)
	category = CategoryForeignSerializer()

	class Meta:
		model = Product
		fields = ('id', 'name', 'brand', 'category')



class ProductDetailSerializer(BaseAPIModelSerializer):
	id = serializers.IntegerField(required=False)
	category = CategoryForeignSerializer()

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['attributes'] = self._get_product_attributes_to_representation(instance)
		return representation

	def _get_product_attributes_to_representation(self, product):
		representation = []
		for category in product.category.get_category_path_qs():
			for attribute in category.attributes.all():
				attr_dict = OrderedDict([
					('id', attribute.id),
					('name', attribute.name),
					('is_attribute_required', attribute.categories.through.objects.get(attribute=attribute, category=category).is_attribute_required),
					# attribute.categoryattribute_set.get(category=category).is_attribute_required
				])
				representation.append(attr_dict)
		for attribute in product.attributes.all():
			attr_dict = OrderedDict([
				('id', attribute.id),
				('name', attribute.name),
				('is_attribute_required', attribute.products.through.objects.get(attribute=attribute, product=product).is_attribute_required),
				# attribute.categoryattribute_set.get(category=category).is_attribute_required
			])
			representation.append(attr_dict)
		return representation

	class Meta:
		model = Product
		fields = ('id', 'name', 'brand', 'category')


class ProductCreateSerializer(BaseAPIModelSerializer):
	id = serializers.IntegerField(required=False)
	attribute_ids_required = APIPrimaryKeyRelatedField(queryset=Attribute.objects.all(), write_only=True, many=True)
	attribute_ids_not_required = APIPrimaryKeyRelatedField(queryset=Attribute.objects.all(), write_only=True, many=True)

	class Meta:
		model = Product
		fields = ('id', 'name', 'brand', 'category', 'attribute_ids_required', 'attribute_ids_not_required')
	
	# def to_internal_value(self, data):
	# 	category_id = data['category']
	# 	data['category'] = Category.objects.get(id=category_id)
	# 	return super().to_internal_value(data)

	def _set_attributes_required_flag(self, product, attributes_required, attributes_not_required):
		product_attributes = product.attributes.through.objects.filter(product=product)

		for product_attribute in product_attributes:
			if product_attribute.attribute in attributes_required:
				product_attribute.is_attribute_required = True
				product_attribute.save()
			elif product_attribute.attribute in attributes_not_required:
				product_attribute.is_attribute_required = False
				product_attribute.save()

	def save(self):
		try:
			super().save()
		except IntegrityError as error:
			message = error.args[0]
			if message.__contains__("unique_name_for_brand"):
				raise ValidationError(f'Another Product with the same name exists for this Brand', 'duplicate_fields', { 'field': 'name' })

	
	def update(self, instance, validated_data):
		super().update(instance, validated_data)

		# Maps for instance's current attributes and request's new attributes.
		current_attrs = { attr.id: attr for attr in instance.get_all_attributes_qs() } # instance.attributes.all() so we get the ancestor categories' attributes
		new_attrs_required = { attr.id: attr for attr in validated_data.pop('attribute_ids_required') }
		new_attrs_not_required = { attr.id: attr for attr in validated_data.pop('attribute_ids_not_required') }

		# # Perform deletions.
		for attr_id, attr in current_attrs.items():
			# if attr_id not in new_attrs:
			instance.attributes.remove(attr)
		
		updated_instance_attrs = { attr.id: attr for attr in instance.get_all_attributes_qs() }
		# # Perform re-creations
		for new_attr_id, new_attr in new_attrs_required.items():
			attr = updated_instance_attrs.get(new_attr_id, None)
			if attr is None:
				instance.attributes.add(new_attr)
		for new_attr_id, new_attr in new_attrs_not_required.items():
			attr = updated_instance_attrs.get(new_attr_id, None)
			if attr is None:
				instance.attributes.add(new_attr)
		
		self._set_attributes_required_flag(instance, list(new_attrs_required.values()), list(new_attrs_not_required.values()))
		
		return instance

	def create(self, validated_data):
		attributes_required = validated_data.pop('attribute_ids_required')
		attributes_not_required = validated_data.pop('attribute_ids_not_required')

		product = Product.objects.create(**validated_data)

		product_categories_attributes = list(product.get_all_attributes_qs())
		for attribute in attributes_required + attributes_not_required:
			if attribute not in product_categories_attributes:
				product.attributes.add(attribute)

		self._set_attributes_required_flag(product, attributes_required, attributes_not_required)

		return product