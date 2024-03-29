from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
import django_filters
from django_filters import rest_framework as filters

from api_internal.views import BaseView
from api_internal.permissions import BaseAPIPermission, StorageRolesWriteElseReadOnlyPermission
from api_internal.serializers.stock import StockItemSerializer, StockItemAddSerializer, StockItemBulkAddSerializer, StockItemBulkUpdateSerializer, StockItemAmountSerializer, StockItemRemoveSerializer

from infra_stock.models.stock_item import StockItem
from infra_auth.models.user import User
from infra_custom.models.location import Location



class StockItemFilter(filters.FilterSet):
	sku = django_filters.NumberFilter(field_name='sku__id', lookup_expr='exact')
	product = django_filters.NumberFilter(field_name='sku__product__id', lookup_expr='exact')
	location = django_filters.NumberFilter(field_name='location__id', method='filter_location_tree')

	def filter_location_tree(self, queryset, field_name, value):
		all_descendant_locations = Location.objects.get(id=value).get_all_descendants_qs()
		return queryset.filter(location__in=all_descendant_locations)

	class Meta:
		model = StockItem
		fields = ['sku', 'location']


class StockItemsBaseView(BaseView):
	permission_classes = (BaseAPIPermission, StorageRolesWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		query = StockItem.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(sku__product__client=self.client)
		
		return query



class StockItemsListView(StockItemsBaseView):
	filter_backends = (filters.DjangoFilterBackend,)
	filterset_class = StockItemFilter
	
	def get_serializer_class(self):
		return StockItemAmountSerializer if self.request.method == 'GET' else StockItemAddSerializer
	
	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['get_full_path_name'] = True
		return context

	def get(self, request):
		items_qs = self.filter_queryset(self.get_queryset())
		item_amount_dicts_qs = items_qs.values('sku', 'location').annotate(amount=Count('id', distinct=True))
		item_amount_list = self.paginator.paginate_queryset((item_amount_dicts_qs), request)

		serializer = self.get_serializer(item_amount_list, many=True)
		return self.paginator.get_paginated_response(serializer.data)
	
	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	

class StockItemsBulkAddView(StockItemsBaseView):
	lookup_url_kwarg = 'id'
	filter_backends = (filters.DjangoFilterBackend,)
	filterset_class = StockItemFilter

	def get_serializer_class(self):
		if self.request.method == 'POST':
			return StockItemBulkAddSerializer
		else:
			return StockItemSerializer
	
	# This is for testing purposes: It makes little sense as a customer-based functionality
	def get(self, request):
		locations = self.paginator.paginate_queryset(self.filter_queryset(self.get_queryset()), request)
		serializer = self.get_serializer(locations, many=True, context={'get_full_path_name': True})
		return self.paginator.get_paginated_response(serializer.data)
	
	def post(self, request):
		serializer = self.get_serializer(data=request.data, many=True)
		serializer.is_valid(raise_exception=True)
		response_data = serializer.save()
		return Response(response_data, status=status.HTTP_201_CREATED)


class StockItemsBulkUpdateView(StockItemsBaseView):
	def get_serializer_class(self):
		return StockItemBulkUpdateSerializer
	
	def post(self, request):
		serializer = self.get_serializer(data=request.data, many=True)
		serializer.is_valid(raise_exception=True)
		response_data = serializer.save()
		return Response(response_data, status=status.HTTP_200_OK)


class StockItemsRemoveView(StockItemsBaseView):
	def get_serializer_class(self):
		return StockItemRemoveSerializer
	
	def post(self, request):
		serializer = self.get_serializer(data=request.data, many=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(status=status.HTTP_200_OK)