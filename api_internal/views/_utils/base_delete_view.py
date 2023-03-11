from django.apps import apps
from rest_framework import serializers, status
from rest_framework.response import Response

from .base_view import BaseView


class BaseDeleteSerializer(serializers.Serializer):
    def to_representation(self, instances_deleted):
        representation = super().to_representation(instances_deleted)
        representation['instances_deleted'] = instances_deleted
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

        if len(instances) == 0:
            serializer = self.get_serializer([])
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)

        instances_deleted = 0
        for instance in instances:
            delete_result = instance.delete()
            # Must detect which of the deleted instances are actually of the model/feature being deleted
            # The total count includes 1:M or N:M relationships deletions
            for model_full_name, model_delete_count in delete_result[1].items():
                [app_label, model_name] = model_full_name.split('.')
                instance_model = apps.get_model(app_label=app_label, model_name=model_name)
                if type(instance) == instance_model:
                    instances_deleted += model_delete_count
        
        serializer = self.get_serializer(instances_deleted)
        return Response(serializer.data, status=status.HTTP_200_OK)