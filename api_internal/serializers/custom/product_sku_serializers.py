from collections import OrderedDict
from rest_framework import serializers
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from infra_custom.models import ProductSku, Attribute, Category, AttributeValue
from api_internal.serializers import APIPrimaryKeyRelatedField
from api_internal.serializers.custom.product_serializers import ProductSerializer



class ProductSkuSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
	product = ProductSerializer()

	class Meta:
		model = ProductSku
		fields = ('id', 'product', 'description', 'is_valid')



class ProductSkuDetailSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
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
	attribute_value_ids = APIPrimaryKeyRelatedField(queryset=AttributeValue.objects.all(), write_only=True, many=True)

	class Meta:
		model = ProductSku
		fields = ('id', 'product', 'description', 'is_valid', 'attribute_value_ids')
	
	# def to_internal_value(self, data):
	# 	category_id = data['category']
	# 	data['category'] = Category.objects.get(id=category_id)
	# 	return super().to_internal_value(data)

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
		current_attrs = { attr.id: attr for attr in instance.get_all_attributes_qs() }
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
		attribute_values = validated_data.pop('attribute_value_ids')
		attribute_value_ids = list(map(lambda av : av.id, attribute_values))
		product_sku = ProductSku.objects.create(**validated_data)
		is_valid = True

		'''1. All Related Attributes with IsRequired = True MUST Have a Value'''
		# sav.attributevalue_id, self.attribute_values.through.objects.all()
		sku_attributes_for_assigned_values = Attribute.objects.filter(attribute_value__id__in=list(map(lambda sav : sav.id, self.attribute_values.all())))
		attribute_ids_for_assigned_values = list(map(lambda attr:attr.id, sku_attributes_for_assigned_values))

		product_related_attributes = self.product.get_attribute_relations_list()
		product_related_attribute_ids = list(map(lambda ar : ar.attribute_id, product_related_attributes))

		missing_values_for_attrs = []

		for attribute_rel in product_related_attributes:
			if attribute_rel.is_attribute_required and attribute_rel.attribute_id not in attribute_ids_for_assigned_values:
				# attr_name = AttributeValue.objects.get(id=attribute_rel.attribute_id).name
				attr_name = sku_attributes_for_assigned_values.get(id=attribute_rel.attribute_id).name
				missing_values_for_attrs.append(attr_name)
		if len(missing_values_for_attrs) > 0:
			is_valid = False
			# raise ValidationError(f'A value must be set for the following attributes: {", ".join(missing_values_for_attrs)}', None, { 'field': 'attribute_values' })
		
		'''2. All self.attribute_values are values for a Related Attribute. (This needs not raise an exception, but merely filter them)'''
		missing_attributes_in_product = [attr_id for attr_id in attribute_ids_for_assigned_values if attr_id not in product_related_attribute_ids]
		if len(missing_attributes_in_product) > 0:
			is_valid = False
			# raise ValidationError(f'There are non-assignable attribute values', None, { 'field': 'attribute_values' })
		
		valid_attribute_values = attribute_values.distinct('attribute_id')
		if len(valid_attribute_values) != len(attribute_values):
			is_valid = False
			# raise ValidationError(f'There are duplicate values for a single attribute.', None, { 'field': 'attribute_values' })
		
		'''
        TODO: Check for duplicates of possible RelatedAttributes combinations 
        So something like a foreach val in attribute_values: ProductSku.object.filter(attribute_values__icontains??=val)
		'''
		existing_product_skus = ProductSku.objects.filter(product=product_sku.product).exclude(id=product_sku.id)
		existing_skus_attribute_values_ids = list(map(lambda sku : sku.get_attribute_values_ids(), existing_product_skus))


		for sku_attr_value_ids in existing_skus_attribute_values_ids:
			if len(set(sku_attr_value_ids).symmetric_difference(set(attribute_value_ids))) == 0:
				is_valid = False
				# raise ValidationError(f'Another SKU for the same Product has the exact same attribute values.', None, { 'field': 'attribute_values' })
		
		print('is_valid', is_valid)
		product_sku.is_valid = is_valid
		product_sku.save()

		# product_categories_attributes = product_sku.get_all_attributes_qs()
		# for attribute in attribute_values:
		# 	# Avoid adding duplicate attributes (i.e. an attribute existing in an ancestor category)
		# 	if attribute not in product_categories_attributes:
		# 		product_sku.attributes.add(attribute)
		# return product_sku