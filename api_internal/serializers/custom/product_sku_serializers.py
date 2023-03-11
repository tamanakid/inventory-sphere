from collections import OrderedDict
from rest_framework import serializers
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from infra_custom.models import ProductSku, Attribute, AttributeValue
from api_internal.serializers import APIPrimaryKeyRelatedField
from api_internal.serializers.custom.product_serializers import ProductSerializer



class ProductSkuSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
	is_valid = serializers.BooleanField(read_only=True)
	product = ProductSerializer()

	class Meta:
		model = ProductSku
		fields = ('id', 'product', 'description', 'is_valid')



class ProductSkuDetailSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
	is_valid = serializers.BooleanField(read_only=True)
	product = ProductSerializer()

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['attributes'] = self._get_product_sku_attributes_to_representation(instance.product)
		representation['attribute_values'] = self._get_product_sku_attribute_values_to_representation(instance)
		return representation
	
	# Copied from ProductDetailSerializer
	def _get_product_sku_attributes_to_representation(self, product):
		representation = []
		for category in product.category.get_category_path_qs():
			for attribute in category.attributes.all():
				attr_dict = OrderedDict([
					('id', attribute.id),
					('attribute_id', attribute.id),
					('name', attribute.name),
					('is_attribute_required', attribute.categories.through.objects.get(attribute=attribute, category=category).is_attribute_required),
				])
				representation.append(attr_dict)
		for attribute in product.attributes.all():
			attr_dict = OrderedDict([
				('id', attribute.id),
				('name', attribute.name),
				('is_attribute_required', attribute.products.through.objects.get(attribute=attribute, product=product).is_attribute_required),
			])
			representation.append(attr_dict)
		return representation
	
	def _get_product_sku_attribute_values_to_representation(self, product_sku):
		representation = []
		for attribute_value_rel in product_sku.attribute_values.through.objects.filter(productsku_id=product_sku.id):
			attribute_value = AttributeValue.objects.get(id=attribute_value_rel.attributevalue_id)
			attr_val_dict = OrderedDict([
				('id', attribute_value.id),
				('name', attribute_value.name),
				('attribute_id', attribute_value.attribute.id),
				('m2m_id', attribute_value_rel.id)
			])
			representation.append(attr_val_dict)
		return representation

	class Meta:
		model = ProductSku
		fields = ('id', 'product', 'description', 'is_valid')


class ProductSkuCreateSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
	is_valid = serializers.BooleanField(read_only=True)
	attribute_value_ids = APIPrimaryKeyRelatedField(queryset=AttributeValue.objects.all(), client_field="attribute__client", write_only=True, many=True)

	class Meta:
		model = ProductSku
		fields = ('id', 'product', 'description', 'is_valid', 'attribute_value_ids')

	def save(self):
		try:
			super().save()
		except IntegrityError as error:
			message = error.args[0]
			if message.__contains__("unique_description_for_product"):
				raise ValidationError(f'Another Product Sku with the same Description exists', 'duplicate_fields', { 'field': 'name' })
			raise
	
	def _check_sku_validity(self, instance, attribute_values):
		is_valid = True

		attribute_value_ids = list(map(lambda attr_val : attr_val.id, attribute_values))

		'''1. All Related Attributes with IsRequired = True MUST Have a Value'''
		attributes = Attribute.objects.filter(attribute_value__id__in=attribute_value_ids)
		attribute_ids = list(map(lambda attr:attr.id, attributes))

		product_category_attributes = instance.product.get_attribute_relations_list()
		product_category_attribute_ids = list(map(lambda ar : ar.attribute_id, product_category_attributes))

		missing_values_for_attrs = []

		for attribute_rel in product_category_attributes:
			if attribute_rel.is_attribute_required and attribute_rel.attribute_id not in attribute_ids:
				attr_name = Attribute.objects.get(id=attribute_rel.attribute_id).name
				missing_values_for_attrs.append(attr_name)
		if len(missing_values_for_attrs) > 0:
			is_valid = False
		
		'''2. All product_sku.attribute_values are values for a Related Attribute. (This needs not raise an exception, but merely filter them)'''
		missing_attributes_in_product = [attr_id for attr_id in attribute_ids if attr_id not in product_category_attribute_ids]
		if len(missing_attributes_in_product) > 0:
			is_valid = False
		
		valid_attribute_values = AttributeValue.objects.filter(id__in=attribute_value_ids).distinct('attribute_id')
		if len(valid_attribute_values) != len(attribute_values):
			is_valid = False
		
		'''
		TODO: Check for duplicates of possible RelatedAttributes combinations 
		So something like a foreach val in attribute_values: ProductSku.object.filter(attribute_values__icontains??=val)
		'''
		existing_product_skus = ProductSku.objects.filter(product=instance.product).exclude(id=instance.id)
		existing_skus_attribute_values_ids = list(map(lambda sku : sku.get_attribute_values_ids(), existing_product_skus))

		for sku_attr_value_ids in existing_skus_attribute_values_ids:
			if len(set(sku_attr_value_ids).symmetric_difference(set(attribute_value_ids))) == 0:
				is_valid = False
		
		instance.attribute_values.set(attribute_value_ids)

		print('is_valid', is_valid)
		instance.is_valid = is_valid
		instance.save()

		return instance
	
	def update(self, instance, validated_data):
		try:
			attribute_values = validated_data.pop('attribute_value_ids')
			super().update(instance, validated_data)
			return self._check_sku_validity(instance, attribute_values)
		except:
			if instance.pk is not None:
				instance.delete()
			raise
	
	def create(self, validated_data):
		product_sku = None
		try:
			attribute_values = validated_data.pop('attribute_value_ids')
			product_sku = ProductSku.objects.create(**validated_data)
			return self._check_sku_validity(product_sku, attribute_values)
		except:
			if product_sku is not None and product_sku.pk is not None:
				product_sku.delete()
			raise
	