from collections import OrderedDict
from logging import Filter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from django.core.exceptions import ValidationError
# TODO: Prolly better to use and handle the DRF ValidationError
# from rest_framework import exceptions

from api_internal.views import BaseView
from api_internal.permissions import BaseAPIPermission, ManagerRolesWriteElseReadOnlyPermission
from api_internal.serializers import CategoryFlatSerializer, CategoryListSerializer, CategoryTreeSerializer, CategoryDetailsSerializer

from infra_custom.models import Category, Attribute, CategoryAttribute



class CategoriesBaseView(BaseView):
	permission_classes = (BaseAPIPermission, ManagerRolesWriteElseReadOnlyPermission)

	def get_queryset(self, *args, **kwargs):
		root_only = kwargs.get('root_only')
		
		query = Category.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(client=self.client)
			
		if root_only:
			query = query.filter(parent=None)
		
		return query


class CategoriesListView(CategoriesBaseView):
	
	def get_serializer_class(self):
		return CategoryFlatSerializer if self.request.method == 'POST' else CategoryListSerializer

	def get(self, request):
		categories = self.paginator.paginate_queryset(self.get_queryset(), request)
		serializer = self.get_serializer(categories, many=True)
		return self.paginator.get_paginated_response(serializer.data)
	
	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoriesTreeView(CategoriesBaseView):
    def get_serializer_class(self):
        return CategoryTreeSerializer
    
    def get(self, request):
        categories = self.get_queryset(root_only=True)
		# Test how to paginate tree lists
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoriesView(CategoriesBaseView):
	lookup_url_kwarg = 'id'

	def get_serializer_class(self):
		return CategoryDetailsSerializer if self.request.method == 'GET' else CategoryFlatSerializer

	def get(self, request, id):
		category = self.get_object()
		serializer = self.get_serializer(category)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	def put(self, request, id):
		category = self.get_object()
		serializer = self.get_serializer(category, data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)


class CategoriesChildrenView(CategoriesBaseView):
	lookup_url_kwarg = 'id'
	
	def get_serializer_class(self):
		return CategoryFlatSerializer
	
	def get(self, request, id):
		category = self.get_object()
		children = category.get_direct_descendants()
		serializer = self.get_serializer(children, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


class CategoriesDeleteView(CategoriesBaseView):
	def post(self, request):
		ids_to_delete = request.data.get('ids', None)
		categories = self.get_queryset().filter(id__in=ids_to_delete)
		for category in categories:
			category.delete()
		return Response(status=status.HTTP_200_OK)