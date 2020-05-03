from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _


class InvalidAuthentication(APIException):
    status_code = 401
    default_code = 401
    default_detail = _('Authentication Failed')


class UnsupportedHTTPMethod(APIException):
    status_code = 405
    default_code = 405
    default_detail = _('Unsupported HTTP method')


class UnsupportedType(APIException):
    status_code = 415
    default_code = 415
    default_detail = _('Invalid Format')


class RequiredParameterDoesNotExist(APIException):
    status_code = 400
    default_code = 601
    default_detail = _('Requirement parameter does not exist')


class ValidateInputFailed(APIException):
    status_code = 400
    default_code = 602
    default_detail = _('Invalid Input')


class UserDoesNotExist(APIException):
    status_code = 404
    default_code = 701
    default_detail = _('User Does Not Exist')


class ProfileDoesNotExist(APIException):
    status_code = 404
    default_code = 702
    default_detail = _('Profile Does Not Exist')


class AccessLogDoesNotExist(APIException):
    status_code = 404
    default_code = 704
    default_detail = _('AccessLog Does Not Exist')


class UserIsNotActive(APIException):
    status_code = 400
    default_code = 705
    default_detail = _('Blocked User')
