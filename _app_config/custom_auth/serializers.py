from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from infra_auth.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customizes JWT default Serializer to add more information about user"""

    # @classmethod
    # def get_token(cls, user):
    #     token = super().get_token(user)

    #     client_serializer = ClientSerializer(data=user.client)
    #     client_serializer.is_valid()

    #     token['email'] = user.email
    #     token['client'] = client_serializer.data
    #     token['is_superuser'] = user.is_superuser
    #     token['is_staff'] = user.is_staff

    #     return token
