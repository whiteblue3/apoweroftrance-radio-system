from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _


class InvalidAuthentication(APIException):
    status_code = 401
    default_code = 401
    default_detail = _('인증 실패')


class UnsupportedHTTPMethod(APIException):
    status_code = 405
    default_code = 405
    default_detail = _('지원하지 않는 HTTP 메소드')


class UnsupportedType(APIException):
    status_code = 415
    default_code = 415
    default_detail = _('지원하지 않는 형식')


class RequiredParameterDoesNotExist(APIException):
    status_code = 400
    default_code = 601
    default_detail = _('필수 입력값 없음')


class ValidateInputFailed(APIException):
    status_code = 400
    default_code = 602
    default_detail = _('입력값 검증 실패')


class UserDoesNotExist(APIException):
    status_code = 404
    default_code = 701
    default_detail = _('존재하지 않는 사용자')


class ProfileDoesNotExist(APIException):
    status_code = 404
    default_code = 702
    default_detail = _('프로필이 존재하지 않음')


class AccessLogDoesNotExist(APIException):
    status_code = 404
    default_code = 704
    default_detail = _('AccessLog가 존재하지 않음')


class UserIsNotActive(APIException):
    status_code = 400
    default_code = 705
    default_detail = _('차단된 사용자')
