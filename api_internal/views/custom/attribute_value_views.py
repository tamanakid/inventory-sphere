from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from api_internal.views import BaseView, BaseDeleteView
from api_internal.permissions import BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission
from api_internal.serializers import AttributeValueGetSerializer, AttributeValueSaveSerializer

from infra_custom.models import AttributeValue


class AttributeValuesBaseView(BaseView):
	permission_classes = (BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		query = AttributeValue.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(attribute__client=self.client)

		if kwargs.get('attribute') is not None:
			query = query.filter(attribute=kwargs.get('attribute'))


		return query


class AttributeValuesListView(AttributeValuesBaseView):

    def get_serializer_class(self):
        return AttributeValueGetSerializer if self.request.method == 'GET' else AttributeValueSaveSerializer
    
    def get(self, request):
        attribute = self.request.query_params.get('attribute', None)
        if attribute is None:
            raise ValidationError('Must specify an attribute')

        attribute_values = self.paginator.paginate_queryset(self.get_queryset(attribute=attribute), request)
        serializer = self.get_serializer(attribute_values, many=True)
        return self.paginator.get_paginated_response(serializer.data)
	
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class AttributeValuesView(AttributeValuesBaseView):
	lookup_url_kwarg = 'id'

	def get_serializer_class(self):
		return AttributeValueGetSerializer if self.request.method == 'GET' else AttributeValueSaveSerializer

	def get(self, request, id):
		attribute_value = self.get_object()
		serializer = self.get_serializer(attribute_value)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def put(self, request, id):
		attribute_value = self.get_object()
		serializer = self.get_serializer(attribute_value, data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)


class AttributeValuesDeleteView(BaseDeleteView, AttributeValuesBaseView):
	pass
