from rest_framework import serializers
from django.core.exceptions import ValidationError

from infra_stock.models.stock_item import StockItem
from infra_custom.models.location import Location
from infra_custom.models.product_sku import ProductSku
from api_internal.serializers import RecursiveField, ChoiceField, BaseAPIModelSerializer, APIPrimaryKeyRelatedField
from api_internal.serializers.custom import LocationFlatSerializer, ProductSkuSerializer



class StockItemSerializer(BaseAPIModelSerializer):
	id = serializers.IntegerField(required=False)
	sku = ProductSkuSerializer()
	location = LocationFlatSerializer()

	class Meta:
		model = StockItem
		fields = ('id', 'sku', 'location')


class StockItemAmountSerializer(BaseAPIModelSerializer):
	id = serializers.IntegerField(required=False)
	sku = ProductSkuSerializer()
	location = LocationFlatSerializer()
	amount = serializers.IntegerField()

	def to_representation(self, instance):
		instance['sku'] = ProductSku.objects.get(id=instance['sku'])
		instance['location'] = Location.objects.get(id=instance['location'])
		representation = super().to_representation(instance)
		return representation

	class Meta:
		model = StockItem
		fields = ('id', 'sku', 'location', 'amount')





class StockItemAddSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)

	class Meta:
		model = StockItem
		fields = ('id', 'sku', 'location')


class StockItemBulkAddSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
	amount = serializers.IntegerField(required=True)

	class Meta:
		model = StockItem
		fields = ('id', 'sku', 'location', 'amount')
	
	def create(self, validated_data):
		amount = validated_data.pop('amount')
		for i in range(amount):
			StockItem.objects.create(**validated_data)
		
		return {
			'sku': validated_data.get('sku').description,
			'location': validated_data.get('location').full_path,
			'amount': amount
		}


class StockItemBulkUpdateSerializer(serializers.ModelSerializer):
	sku = APIPrimaryKeyRelatedField(queryset=ProductSku.objects.all(), client_field="product__client", write_only=True, many=False)
	location_from = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), client_field="level__client", write_only=True, many=False)
	location_to = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), client_field="level__client", write_only=True, many=False)
	amount = serializers.IntegerField(required=True)

	class Meta:
		model = StockItem
		fields = ('sku', 'location_from', 'location_to', 'amount')

	# This is a relocation ("update") process
	def create(self, validated_data):
		amount = validated_data.pop('amount')
		sku = validated_data.pop('sku')
		location_from = validated_data.pop('location_from')
		location_to = validated_data.pop('location_to')

		updateable_instances = StockItem.objects.filter(sku=sku, location=location_from)
		updateable_amount = updateable_instances.count()

		if (updateable_amount < amount):
			raise ValidationError(f'This Location only contains {updateable_amount} updateable units for the specified SKU', 'no_stock', { 'field': 'amount' })
		
		instances_to_update = StockItem.objects.filter(id__in=list(updateable_instances.values_list('pk', flat=True)[:amount]))
		instances_to_update.update(location=location_to)

		return list(map(lambda instance : {
			'sku': instance.sku.description,
			'location': instance.location.full_path,
			'amount': amount
		}, instances_to_update))


class StockItemRemoveSerializer(serializers.ModelSerializer):
	sku = APIPrimaryKeyRelatedField(queryset=ProductSku.objects.all(), client_field="product__client", write_only=True, many=False)
	location = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), client_field="level__client", write_only=True, many=False)
	amount = serializers.IntegerField(required=True)

	class Meta:
		model = StockItem
		fields = ('sku', 'location', 'amount')
	
	# This is a Remove ("delete") process
	def create(self, validated_data):
		amount = validated_data.pop('amount')
		sku = validated_data.pop('sku')
		location = validated_data.pop('location')

		removable_instances = StockItem.objects.filter(sku=sku, location=location)
		removable_amount = removable_instances.count()

		if (removable_amount < amount):
			raise ValidationError(f'This Location only contains {removable_amount} removable units for the specified SKU', 'no_stock', { 'field': 'amount' })
		
		instances_to_remove = StockItem.objects.filter(id__in=list(removable_instances.values_list('pk', flat=True)[:amount]))
		instances_to_remove.delete()
