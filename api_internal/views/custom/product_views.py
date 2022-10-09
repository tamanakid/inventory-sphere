from rest_framework import status
from rest_framework.response import Response

import django_filters
from django_filters import rest_framework as filters

from api_internal.views import BaseView, BaseDeleteView
from api_internal.permissions import BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission
from api_internal.serializers import ProductSerializer, ProductDetailSerializer, ProductCreateSerializer

from infra_custom.models import Product


class ProductFilter(filters.FilterSet):
	name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
	brand = django_filters.CharFilter(field_name='brand', lookup_expr='icontains')
	category = django_filters.NumberFilter(field_name='category__id', lookup_expr='exact')

	class Meta:
		model = Product
		fields = ['name', 'brand', 'category']


class ProductsBaseView(BaseView):
	permission_classes = (BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		query = Product.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(client=self.client)
		
		return query


# TODO: There will be a need to get all the attributes a product will support:
# This will encompass attributes related to the product and ALL it's ancestor categories
# This is likely better in its own endpoint

class ProductsListView(ProductsBaseView):
	filter_backends = (filters.DjangoFilterBackend,)
	filterset_class = ProductFilter

	def get_serializer_class(self):
		return ProductSerializer if self.request.method == 'GET' else ProductCreateSerializer

	def get(self, request):
		products = self.paginator.paginate_queryset(self.filter_queryset(self.get_queryset()), request)
		serializer = self.get_serializer(products, many=True)
		return self.paginator.get_paginated_response(serializer.data)
		# return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)



class ProductsView(ProductsBaseView):
	lookup_url_kwarg = 'id'

	def get_serializer_class(self):
		return ProductDetailSerializer if self.request.method == 'GET' else ProductCreateSerializer

	def get(self, request, id):
		product = self.get_object()
		serializer = self.get_serializer(product)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def put(self, request, id):
		product = self.get_object()
		serializer = self.get_serializer(product, data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsDeleteView(BaseDeleteView, ProductsBaseView):
	pass