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

import django_filters
from django_filters import rest_framework as filters

from api_internal.views import BaseView, BaseDeleteView
from api_internal.permissions import BaseAPIPermission, ManagerRolesWriteElseReadOnlyPermission
from api_internal.serializers import CategoryFlatSerializer, CategoryListSerializer, CategoryTreeSerializer, CategoryDetailsSerializer

from infra_custom.models import Category, Attribute, CategoryAttribute



class CategoryFilter(filters.FilterSet):
	name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
	attributes = django_filters.NumberFilter(field_name='attributes__id', lookup_expr='exact')

	class Meta:
		model = Category
		fields = ['name', 'attributes']



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
	filter_backends = (filters.DjangoFilterBackend,)
	filterset_class = CategoryFilter
	
	def get_serializer_class(self):
		return CategoryFlatSerializer if self.request.method == 'POST' else CategoryListSerializer

	def get(self, request):
		categories = self.paginator.paginate_queryset(self.filter_queryset(self.get_queryset()), request)
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


class CategoriesDeleteView(BaseDeleteView, CategoriesBaseView):
	pass