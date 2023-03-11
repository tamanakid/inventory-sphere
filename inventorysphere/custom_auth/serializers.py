from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Customizes JWT default Serializer to add more information about user

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['client_id'] = user.client.id
        token['role'] = user.role

        return token
