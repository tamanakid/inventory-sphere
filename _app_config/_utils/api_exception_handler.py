from http import HTTPStatus

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import exceptions as drf_exceptions #, ValidationError as DRFValidationError, ErrorDetail
from rest_framework.views import exception_handler as drf_exception_handler


# https://rednafi.github.io/reflections/uniform-error-response-in-django-rest-framework.html
# https://gist.github.com/twidi/9d55486c36b6a51bdcb05ce3a763e79f


http_code_to_message = { v.value: v.description for v in HTTPStatus}

"""
Django models may raise ``ValidationError``s in the ``save`` method.
This exception is not managed by Django Rest Framework because it occurs after its validation process.
The following exception handler override converts Django's ``ValidationError`` to a DRF one.
"""
def api_exception_handler(exception, context):
    exception = convert_to_drf_exception(exception)

    response = drf_exception_handler(exception, context)
    if response is not None:
        error_payload = {
            "error": {
                "status_code": 0,
                "status_message": "",
                "details": [],
            }
        }
        error = error_payload["error"]
        status_code = response.status_code

        error["status_code"] = status_code
        error["status_message"] = http_code_to_message[status_code]
        error["details"] = response.data

        response.data = error_payload

    return response



def convert_to_drf_exception(exception):
    # Convert Django's ValidationError
    if isinstance(exception, DjangoValidationError):
        if hasattr(exception, "message"):
            exception_params = exception.params or {}
            details = [{
                'detail_message': exception.message or "",
                'detail_code': exception.code or "",
                'detail_show_message': True if exception.code is None else exception_params.get('show_message'), # TODO: Convert to boolean (error base serializer?)
                'detail_field': exception_params.get('field')
            }]
        # If "messages" (ilst) or "message_dict" are found instead of a plain message:
        # Attempt to adjust the code raising the exception to pass a simple "message", instead of refactoring these scenarios
        elif hasattr(exception, "messages"):
            # detail = { '_root': msg for msg in exception.messages }
            details = 'An error has occured'
        elif hasattr(exception, "message_dict"):
            # detail = exception.message_dict
            details = 'An error has occured'
        else:
            details = 'An error has occured'
        
        exception = drf_exceptions.ValidationError(detail=details)
    
    # The main "details" body construction should be encompassed in only one conditional statement
    elif isinstance(exception, drf_exceptions.APIException):
        if exception.detail is not None:
            details = []
            for field, detail_list in exception.detail.items():
                for detail in detail_list:
                    details.append({
                        'detail_message': detail.__str__(),
                        'detail_code': detail.code,
                        'detail_show_message': False,
                        'detail_field': field
                    })
            exception = exception.__class__(detail=details)
    
    return exception



# Idea:
# details should be an array of dictionaries with:
# * detail_field (string): field involved in failure (Naah, LET'S ACTUALLY TRY TO REMOVE THE FIELD FROM THE OTHER EXCEPTIONS -> Make it OPTIONAL: Allows client-side to emphasize failing field)
# * detail_code (string): code from ErrorDetail class, which would allow either the client-side or the server-side to MAKE ERROR MESSAGES UNIFORM
# * detail_message (string): Full message coming either from DRF or application code
# * detail_show_message (boolean): if True, "error_detail_message" is shown instead of default message for "detail_code" -> (DEFAULTS TO TRUE IF detail_code is None)