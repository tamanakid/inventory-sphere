from collections import OrderedDict
from rest_framework import serializers
from django.core.exceptions import ValidationError

from infra_auth.models.user import User
from infra_custom.models import Location
from api_internal.serializers import BaseAPIModelSerializer, APIPrimaryKeyRelatedField


class UserSerializer(BaseAPIModelSerializer):
	id = serializers.IntegerField(required=False)

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['locations'] = self._get_user_locations(instance)
		return representation
	
	def _get_user_locations(self, instance):
		representation = []
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
    location_ids = APIPrimaryKeyRelatedField(queryset=Location.objects.all(), write_only=True, many=True, client_field='level__client')
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'location_ids', 'password')
    
    def _check_locations_validity(self, locations, posting_user):
        # Is already enforced by permission classes
        if not posting_user.is_storage_user:
            raise ValidationError(f'Only Managers can add new Users')
        
        if posting_user.role == User.Role.INVENTORY_MANAGER:
            return
            
        posting_user_locations = posting_user.locations.all()
        for location in locations:
            if not location.level.is_root_storage_level:
                raise ValidationError(f'Locations can only be added to a Storage Employee if these are RSLs', 'non_rsl_location', { 'field': 'location_ids' })
            if location not in posting_user_locations:
                raise ValidationError(f'Locations can only be added to a Storage Employee by managers of said locations', 'add_user_to_location_auth', { 'field': 'location_ids' })
        return
        
    
    def create(self, validated_data):
        locations = validated_data.pop('location_ids')
        posting_user = User.objects.get(id=self.context['request'].user.id)
        self._check_locations_validity(locations, posting_user)

        user = User.objects.create(**validated_data)

        password = validated_data.get('password', None)
        if password is not None:
            user.set_password(password)
        user.save()

        for location in locations:
            user.locations.add(location)
        return user


    def update(self, user_instance, validated_data):
        current_locations = { loc.id: loc for loc in user_instance.locations.all() }
        new_locations = { loc.id: loc for loc in validated_data.pop('location_ids') }
        
        posting_user = User.objects.get(id=self.context['request'].user.id)
        self._check_locations_validity(list(new_locations.values()), posting_user)

        super().update(user_instance, validated_data)

        # Perform creations and updates.
        for new_loc_id, new_loc in new_locations.items():
            loc = current_locations.get(new_loc_id, None)
            if loc is None:
                user_instance.locations.add(new_loc)

        # Perform deletions.
        for loc_id, loc in current_locations.items():
            if loc_id not in new_locations:
                user_instance.locations.remove(loc)

        return user_instance