from collections import OrderedDict
from rest_framework import serializers
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from infra_auth.models.user import User
from infra_custom.models import Product, Location
from api_internal.serializers import BaseAPIModelSerializer, APIPrimaryKeyRelatedField
from api_internal.serializers.custom.category_serializers import CategoryForeignSerializer
# from api_internal.serializers.custom.location_serializers import LocationForeignSerializer




# class UserLocationSerializer(serializers.ModelSerializer):
# 	id = serializers.IntegerField(required=False)
# 	is_root_storage_level = serializers.ReadOnlyField(source='level.is_root_storage_level')

# 	def to_representation(self, m2m_manager):
# 		instance = m2m_manager.instance
# 		representation = super().to_representation(instance)
# 		# Would need an instance lookup if provided a non-instance object (i.e. as in the POST method)
# 		if self.context.get('get_full_path_name', False):
# 			representation['name'] = instance.get_full_path() 
# 		return representation

# 	class Meta:
# 		model = Location
# 		fields = ('id', 'name', 'level', 'is_root_storage_level', 'parent')



class UserSerializer(BaseAPIModelSerializer):
	id = serializers.IntegerField(required=False)
	# locations = UserLocationSerializer()

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['locations'] = self._get_user_locations(instance)
		return representation
	
	def _get_user_locations(self, instance):
		representation = []
		# user_locations = list(map(lambda ul : ul.location, instance.locations.through.objects.filter(user=instance)))
		# for user_location in instance.locations.through.objects.filter(user=instance):
		# 	location = user_location.location
		for location in instance.locations.filter(user=instance):
			location_dict = OrderedDict([
				('id', location.id),
				('name', location.name),
				('full_path', location.full_path),
			])
			representation.append(location_dict)
		return representation

	class Meta:
		model = User
		fields = ('id', 'email', 'first_name', 'last_name', 'role', 'locations')



class UserCreateSerializer(BaseAPIModelSerializer):
    id = serializers.IntegerField(required=False)
    location_ids = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), write_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'location_ids')
    
    def create(self, validated_data):
        locations = validated_data.pop('location_ids')
        user = User.objects.create(**validated_data)

        product_categories_attributes = user.get_all_attributes_qs()
        for location in locations:
            if location not in product_categories_attributes:
                user.attributes.add(location)
        return user