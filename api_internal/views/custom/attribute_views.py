from rest_framework import status
from rest_framework.response import Response

from api_internal.views import BaseView
from api_internal.permissions import BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission
from api_internal.serializers import AttributeSerializer, AttributeWithValuesListSerializer

from infra_custom.models import Attribute


class AttributesBaseView(BaseView):
	permission_classes = (BaseAPIPermission, InventoryManagerWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		query = Attribute.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(client=self.client)
		
		return query


class AttributesListView(AttributesBaseView):

    def get_serializer_class(self):
        return AttributeSerializer
    
    def get(self, request):
        attributes = self.paginator.paginate_queryset(self.get_queryset(), request)
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


class AttributesDeleteView(AttributesBaseView):
	def get_serializer_class(self):
		return AttributeSerializer
	
	def post(self, request):
		ids_to_delete = request.data.get('ids', None)
		attributes = self.get_queryset().filter(id__in=ids_to_delete)
		for attribute in attributes:
			attribute.delete()
		return Response(status=status.HTTP_200_OK)