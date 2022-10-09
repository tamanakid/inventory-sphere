from rest_framework import status
from rest_framework.response import Response

import django_filters
from django_filters import rest_framework as filters

from api_internal.views import BaseView, BaseDeleteView
from api_internal.permissions import BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission
from api_internal.serializers import AttributeSerializer, AttributeWithValuesListSerializer

from infra_custom.models import Attribute


class AttributeFilter(filters.FilterSet):
	name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

	class Meta:
		model = Attribute
		fields = ['name']


class AttributesBaseView(BaseView):
	permission_classes = (BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		query = Attribute.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(client=self.client)
		
		return query


# TODO: There will be a need to get all the attributes a category will support:
# This will encompass attributes related to the category and ALL it's ancestors'
# This is likely better in its own endpoint

class AttributesListView(AttributesBaseView):
	filter_backends = (filters.DjangoFilterBackend,)
	filterset_class = AttributeFilter

	def get_serializer_class(self):
		return AttributeSerializer

	def get(self, request):
		attributes = self.paginator.paginate_queryset(self.filter_queryset(self.get_queryset()), request)
		serializer = self.get_serializer(attributes, many=True)
		return self.paginator.get_paginated_response(serializer.data)
		# return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)



class AttributesView(AttributesBaseView):
	lookup_url_kwarg = 'id'

	def get_serializer_class(self):
		return AttributeWithValuesListSerializer if self.request.method == 'GET' else AttributeSerializer

	def get(self, request, id):
		attribute = self.get_object()
		serializer = self.get_serializer(attribute)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def put(self, request, id):
		attribute = self.get_object()
		serializer = self.get_serializer(attribute, data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)


class AttributesDeleteView(BaseDeleteView, AttributesBaseView):
	pass