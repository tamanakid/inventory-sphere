from rest_framework import serializers, status
from rest_framework.response import Response

from .base_view import BaseView


class BaseDeleteSerializer(serializers.Serializer):
    def to_representation(self, instances):
        representation = super().to_representation(instances)
        representation['instances_deleted'] = len(instances)
        return representation


# Any class inheriting from the BaseDeleteView must either
# 1. Be a subclass of a BaseView which implements get_queryset()
# 2. Implement its own get_queryset() [Least recommended approach]

class BaseDeleteView(BaseView):
    def get_serializer_class(self):
        return BaseDeleteSerializer

    def post(self, request):
        ids_to_delete = request.data.get('ids', None)
        instances = self.get_queryset().filter(id__in=ids_to_delete)

        for instance in instances:
            instance.delete()
        
        serializer = self.get_serializer(instances)
        return Response(serializer.data, status=status.HTTP_200_OK)