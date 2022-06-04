from django.http import Http404
from django.core import exceptions as django_exceptions # import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework import exceptions as drf_exceptions #, ValidationError as DRFValidationError, ErrorDetail
from rest_framework.views import exception_handler as drf_exception_handler


# https://rednafi.github.io/reflections/uniform-error-response-in-django-rest-framework.html
# https://gist.github.com/twidi/9d55486c36b6a51bdcb05ce3a763e79f


"""
Django models may raise ``ValidationError``s in the ``save`` method.
This exception is not managed by Django Rest Framework because it occurs after its validation process.
The following exception handler override converts Django's ``ValidationError`` to a DRF one.
"""
def api_exception_handler(exception, context):
    print(exception.__str__())
    exception = convert_to_drf_exception(exception)

    response = drf_exception_handler(exception, context)
    if response is not None:
        # error_payload = { "errors": response.data }
        # errors = error_payload["errors"] = response.data
        # response.data = error_payload
        response.data = { "errors": response.data }

    return response



def convert_to_drf_exception(exception):
    # Convert Django's ValidationError
    if isinstance(exception, django_exceptions.ValidationError):
        if hasattr(exception, "message"):
            exception_params = exception.params or {}
            response_errors = [{
                'message': exception.message or "",
                'code': exception.code or "",
                'show_message': True if exception.code is None else exception_params.get('show_message'), # TODO: Convert to boolean (error base serializer?)
                'field': exception_params.get('field')
            }]
        # If "messages" (ilst) or "message_dict" are found instead of a plain message:
        # Attempt to adjust the code raising the exception to pass a simple "message", instead of refactoring these scenarios
        elif hasattr(exception, "messages"):
            # detail = { '_root': msg for msg in exception.messages }
            response_errors = [{ 'code': 'generic_error' }]
        elif hasattr(exception, "message_dict"):
            # detail = exception.message_dict
            response_errors = [{ 'code': 'generic_error' }]
        else:
            response_errors = [{ 'code': 'generic_error' }]
        
        exception = drf_exceptions.ValidationError(detail=response_errors)
    
    elif isinstance(exception, drf_exceptions.AuthenticationFailed):
        response_errors = [{
            'message': "",
            'code': "authentication_failed",
            'show_message': False,
            'field': None
        }]
        exception = drf_exceptions.APIException(detail=response_errors)
        exception.status_code = status.HTTP_401_UNAUTHORIZED
    
    elif isinstance(exception, Http404):
        response_errors = [{
            'message': "",
            'code': "does_not_exist",
            'show_message': False,
            'field': None
        }]
        exception = drf_exceptions.APIException(detail=response_errors)
        exception.status_code = status.HTTP_404_NOT_FOUND
    
    elif isinstance(exception, django_exceptions.PermissionDenied):
        response_errors = [{
            'message': "",
            'code': "permission_denied",
            'show_message': False,
            'field': None
        }]
        exception = drf_exceptions.APIException(detail=response_errors)
        exception.status_code = status.HTTP_403_FORBIDDEN

    # TODO: Confirm the main error body construction should be encompassed in only one conditional statement
    elif isinstance(exception, drf_exceptions.APIException):
        if exception.detail is not None:
            response_errors = []
            if isinstance(exception.detail, dict):
                for field, error_list in exception.detail.items():
                    for error in error_list:
                        response_errors.append({
                            'message': error.__str__(),
                            'code': error.code,
                            'show_message': False,
                            'field': field
                        })
            elif isinstance(exception.detail, drf_exceptions.ErrorDetail):
                response_errors.append({
                    'message': exception.detail.__str__(),
                    'code': exception.detail.code,
                    'show_message': False,
                    'field': None
                })
            status_code = exception.status_code
            exception = exception.__class__(detail=response_errors)
            exception.status_code = status_code
    
    # Default handler for unregistered exceptions
    # If a particular Exception needs to be handled differently, create a new conditional statement (In the meantime)
    else:
        response_errors = [{
            'message': "",
            'code': "generic_error",
            'show_message': False,
            'field': None
        }]
        exception = drf_exceptions.APIException(detail=response_errors)
        exception.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return exception
