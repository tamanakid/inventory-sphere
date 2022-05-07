from rest_framework import serializers


## Definitely breaks
class BaseAPISerializer(serializers.Serializer):
    def create(self, validated_data):
        validated_data['client'] = self.request.user.client
        return super().create(validated_data)


class BaseAPIModelSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        kwargs['client'] = self.context['client']
        return super().save(**kwargs)
