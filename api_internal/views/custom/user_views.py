from rest_framework import status
from rest_framework.response import Response
import django_filters
from django_filters import rest_framework as filters

from api_internal.views import BaseView, BaseDeleteView
from api_internal.permissions import BaseAPIPermission, ManagerRolesPermission
from api_internal.serializers.custom import UserSerializer, UserCreateSerializer

from infra_auth.models.user import User
from infra_custom.models.location import Location



class UserFilter(filters.FilterSet):
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    role = django_filters.CharFilter(field_name='role', lookup_expr='exact')
    locations = django_filters.ModelMultipleChoiceFilter(
        field_name='locations__id',
        to_field_name='id',
        queryset=Location.objects.filter(level__is_root_storage_level=True)
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'locations']


class UsersBaseView(BaseView):
	permission_classes = (BaseAPIPermission, ManagerRolesPermission)

	def get_queryset(self, *args, **kwargs):
		query = User.objects.all()

		if not self.request.user.is_superuser:
			query = query.filter(client=self.client)
        
		if self.request.user.role == User.Role.INVENTORY_MANAGER:
			query = query
		elif self.request.user.role == User.Role.STORAGE_MANAGER:
			user = User.objects.get(id=self.request.user.id)
			user_locations = user.locations.filter(user=user)
			query = query.filter(locations__in=user_locations).distinct('id')
		else:
			query = User.objects.none()
			
		return query



class UsersListView(UsersBaseView):
	filter_backends = (filters.DjangoFilterBackend,)
	filterset_class = UserFilter
	
	def get_serializer_class(self):
		return UserSerializer if self.request.method == 'GET' else UserCreateSerializer

	def get(self, request):
		users = self.paginator.paginate_queryset(self.filter_queryset(self.get_queryset()), request)
		serializer = self.get_serializer(users, many=True)
		return self.paginator.get_paginated_response(serializer.data)

	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class UsersView(UsersBaseView):
	lookup_url_kwarg = 'id'
	
	def get_serializer_class(self):
		return UserSerializer if self.request.method == 'GET' else UserCreateSerializer

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


class UsersDeleteView(BaseDeleteView, UsersBaseView):
	pass