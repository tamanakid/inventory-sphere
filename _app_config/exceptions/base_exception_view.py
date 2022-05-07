from abc import ABC, abstractmethod

from django.core import exceptions as django_exceptions

from rest_framework import exceptions as drf_exceptions, status
from rest_framework.views import APIView, exception_handler



def parse_exception_to_drf(exc, context):
    if isinstance(exc, django_exceptions.ValidationError):
        return drf_exceptions.ValidationError(exc.message)
    return exc


'''
Since "standard" DRF exception handling is project-scoped instead of app-scoped
Our strategy consists of overriding APIView's "handle_exception"
'''
class BaseExceptionView(ABC, APIView):
    # Overridable by each application's BaseView
    # Defaulted to standard views' exception_handler
    def exception_handler(self, exc, context):
        # parses non-DRF exceptions (i.e., django) to be manageable by DRF's default handler
        exc = parse_exception_to_drf(exc, context)

        # Call DRF's default exception handler first,
        # to get the standard error response.
        response = exception_handler(exc, context)

        # Now add the HTTP status code to the response.
        if response is not None:
            response.data['status_code'] = response.status_code

        return response


    def handle_exception(self, exc):
        """
        Handle any exception that occurs, by returning an appropriate response,
        or re-raising the error.
        """
        if isinstance(exc, (drf_exceptions.NotAuthenticated,
                            drf_exceptions.AuthenticationFailed)):
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                exc.auth_header = auth_header
            else:
                exc.status_code = status.HTTP_403_FORBIDDEN

        context = self.get_exception_handler_context()
        response = self.exception_handler(exc, context) # instead of "exception_handler(exc, context)"

        if response is None:
            self.raise_uncaught_exception(exc)

        response.exception = True
        return response