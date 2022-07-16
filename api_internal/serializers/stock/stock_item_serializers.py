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


class StockItemAddBulkSerializer(serializers.ModelSerializer):
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


class StockItemUpdateBulkSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
	sku = ProductSkuSerializer()
	location_from = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), client_field="level__client", write_only=True, many=False)
	location_to = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), client_field="level__client", write_only=True, many=False)
	amount = serializers.IntegerField(required=True)

	class Meta:
		model = StockItem
		fields = ('id', 'sku', 'location_from', 'location_to', 'amount')

	def update(self, instance, validated_data):
		amount = validated_data.pop('amount')

		sku = validated_data.get('sku')
		location_from = validated_data.get('location_from')
		amount_updateable = StockItem.objects.filter(sku=sku, location=location_from)
		if (amount_updateable < amount):
			raise ValidationError(f'This Location only contains {amount_updateable} updateable units for the specified SKU', 'no_stock', { 'field': 'amount' })

		validated_data['location'] = validated_data.pop('location_to')
		super().update(instance, validated_data)


class StockItemDeleteSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=False)
	sku = ProductSkuSerializer()
	location_from = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), client_field="level__client", write_only=True, many=False)
	location_to = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), client_field="level__client", write_only=True, many=False)
	amount = serializers.IntegerField(required=True)

	class Meta:
		model = StockItem
		fields = ('id', 'sku', 'location', 'amount')