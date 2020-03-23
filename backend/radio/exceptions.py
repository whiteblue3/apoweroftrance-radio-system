from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from .error import *


def core_exception_handler(exc, context):
    # If an exception is thrown that we don't explicitly handle here, we want
    # to delegate to the default exception handler offered by DRF. If we do
    # handle this exception type, we will still want access to the response
    # generated by DRF, so we get that response up front.
    response = exception_handler(exc, context)
    handlers = {
        'AuthenticationFailed': _handle_generic_error,
        'InvalidAuthentication': _handle_generic_error,
        'UnsupportedHTTPMethod': _handle_generic_error,
        'UnsupportedType': _handle_generic_error,
        'RequiredParameterDoesNotExist': _handle_generic_error,
        'ValidateInputFailed': _handle_generic_error,
        'UserDoesNotExist': _handle_generic_error,
        'ProfileDoesNotExist': _handle_generic_error,
        'UserIsNotActive': _handle_generic_error,
        'AccessLogDoesNotExist': _handle_generic_error,
        'ValidationError': _handle_generic_error
    }
    # This is how we identify the type of the current exception. We will use
    # this in a moment to see whether we should handle this exception or let
    # Django REST Framework do its thing.
    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        # If this exception is one that we can handle, handle it. Otherwise,
        # return the response generated earlier by the default exception
        # handler.
        return handlers[exception_class](exc, context, response)
    else:
        if response is not None:
            response.data = {
                'errors': response.data
            }
            # if "data" in response:
            #     response.data = {
            #         'errors': response.data
            #     }
            # else:
            #     response.data = {
            #         'errors': response.data
            #     }

    return response


def _handle_generic_error(exc, context, response):
    # This is the most straightforward exception handler we can create.
    # We take the response generated by DRF and wrap it in the `errors` key.
    try:
        response.data = {
            'errors': response.data
        }
    except Exception:
        exception = ValidationError(exc)
        print(exc, context, response)
        response = exception
        # response = {
        #     "data": {
        #         "errors": exception
        #     }
        # }

    # code = response.data['detail'].code
    # message = response.data['detail']
    #
    # response.data = {
    #     # 'code': str(code).zfill(4),
    #     'code': code,
    #     'message': message
    # }

    return response
