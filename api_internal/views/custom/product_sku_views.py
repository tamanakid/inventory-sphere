from rest_framework import status
from rest_framework.response import Response

import django_filters
from django_filters import rest_framework as filters

from api_internal.views import BaseView, BaseDeleteView
from api_internal.permissions import BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission
from api_internal.serializers import ProductSkuSerializer, ProductSkuDetailSerializer, ProductSkuCreateSerializer

from infra_custom.models import ProductSku, Product


class ProductSkuFilter(filters.FilterSet):
	description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')
	product = django_filters.NumberFilter(field_name='product__id', lookup_expr='exact')
	is_valid = django_filters.BooleanFilter(field_name='is_valid')

	class Meta:
		model = ProductSku
		fields = ['description', 'product', 'is_valid']


class ProductSkusBaseView(BaseView):
	permission_classes = (BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		query = ProductSku.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(product__client=self.client)
		
		return query


# TODO: There will be a need to get all the attributes a product will support:
# This will encompass attributes related to the product and ALL it's ancestor categories
# This is likely better in its own endpoint

class ProductSkusListView(ProductSkusBaseView):
	filter_backends = (filters.DjangoFilterBackend,)
	filterset_class = ProductSkuFilter

	def get_serializer_class(self):
		return ProductSkuSerializer if self.request.method == 'GET' else ProductSkuCreateSerializer

	def get(self, request):
		product_skus = self.paginator.paginate_queryset(self.filter_queryset(self.get_queryset()), request)
		serializer = self.get_serializer(product_skus, many=True)
		return self.paginator.get_paginated_response(serializer.data)
		# return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)



class ProductSkusView(ProductSkusBaseView):
	lookup_url_kwarg = 'id'

	def get_serializer_class(self):
		return ProductSkuDetailSerializer if self.request.method == 'GET' else ProductSkuCreateSerializer

	def get(self, request, id):
		product_sku = self.get_object()
		serializer = self.get_serializer(product_sku)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def put(self, request, id):
		product_sku = self.get_object()
		serializer = self.get_serializer(product_sku, data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)


class ProductSkusDeleteView(BaseDeleteView, ProductSkusBaseView):
	pass