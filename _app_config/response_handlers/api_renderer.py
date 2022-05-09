from http import HTTPStatus

from rest_framework.renderers import JSONRenderer
from rest_framework import exceptions as drf_exceptions 


http_status_dict = { status.value: status.description for status in HTTPStatus }

# https://stackoverflow.com/a/48956238
class APIRenderer(JSONRenderer):
    
    def render(self, data, accepted_media_type=None, renderer_context=None):

        if isinstance(data, list):
            errors = None
            data_without_errors = data

        elif isinstance(data, dict):
            errors = data.get('errors')
            data_without_errors = {}
            for key, value in data.items():
                if key not in ('errors'):
                    data_without_errors[key] = value

        elif data is None:
            errors = None
            data_without_errors = None

        else:
            raise drf_exceptions.APIException('Response Data must be either a Dictionary or List')

        # TODO: Evaluate whether it is necessary to send the status code and message as part of the response body
        # It's likely not: This info is part of the response headers
        status_code = renderer_context.get('response').status_code

        response_data = {
            'status_code': status_code,
            'status_message': http_status_dict[status_code],
            'data': data_without_errors,
            'errors': errors,
        }

        getattr(renderer_context.get('view').get_serializer().Meta,'resource_name', 'objects')

        # call super to render the response
        response = super(APIRenderer, self).render(response_data, accepted_media_type, renderer_context)

        return response