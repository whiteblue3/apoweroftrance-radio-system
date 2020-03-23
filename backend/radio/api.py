import logging
import os
import json
import secrets
from datetime import datetime, timedelta
import urllib.parse
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import mixins, generics
from rest_framework.response import Response
from .serializers.model import (
    AccessLogSerializer
)
from .models import Profile
from .access_log import *
from .exceptions import ProfileDoesNotExist
from . import aes

logger = logging.getLogger(__name__)


def response_error(error, status=None):
    header = {"Server": "server"}
    data = {"error": error}

    response = Response(data, headers=header, status=status)
    return response


def response_json(payload, status=None):
    header = {"Server": "server"}
    data = {"payload": payload}

    response = Response(data, headers=header, status=status)
    return response


def response_html(html, status=None):
    header = {"Server": "server"}

    return Response(html, headers=header, status=status)


def response_url(url):
    return HttpResponseRedirect(url)


def response_http(contents, *args, **kwargs):
    return HttpResponse(contents, *args, **kwargs)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def accesslog(request, access_type, status, email, ip):
    data = {
        'email': email,
        'ip_address': ip,
        'request': '%s %s' % (request.method, request.get_full_path()),
        'request_body': str(request.data),
        'access_type': access_type,
        'access_status': status
    }

    """Remove authenticate information for security"""
    if access_type is ACCESS_TYPE_AUTHENTICATE:
        data.pop('request_body')

    accesslog_serializer = AccessLogSerializer(data=data)
    accesslog_serializer.is_valid(raise_exception=True)
    accesslog_serializer.save()


def get_module_config():
    return os.environ.get("DJANGO_SETTINGS")


def get_profile(email):
    try:
        # We use the `select_related` method to avoid making unnecessary
        # database calls.
        profile = Profile.objects.select_related('user').get(
            user__email=email
        )
    except Profile.DoesNotExist:
        raise ProfileDoesNotExist
    return profile


def generate_password(length=11, charset="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()"):
    return "".join([secrets.choice(charset) for _ in range(0, length)])


def send_reset_password_email(email):
    now = datetime.now()
    new_password = generate_password()
    expire = now + timedelta(minutes=30)
    confirm_data = {
        'email': email,
        'date': now.isoformat(),
        'password': new_password,
        'expire': expire.isoformat()
    }
    json_encoded = json.dumps(confirm_data)
    encrypted_data = aes.aes_encrypt(json_encoded)

    if "local" in get_module_config():
        domain_url = "127.0.0.1:8000"
    elif "dev" in get_module_config():
        domain_url = "radio-dev.apoweroftrance.com"
    elif "stage" in get_module_config():
        domain_url = "radio-stage.apoweroftrance.com"
    else:
        domain_url = "radio.apoweroftrance.com"

    base_url = "https://%s/v1/user/confirm_reset_password" % domain_url
    confirm_link = "%s?auth_code=%s" % (base_url, urllib.parse.quote_plus(encrypted_data))

    email_body = "회원님 안녕하세요.\n" \
                 "\n" \
                 "비밀번호 재설정을 요청하셨습니다.\n" \
                 "임시 비밀번호는 %s 입니다\n" \
                 "아래의 링크를 눌러 비밀번호를 재설정을 완료하세요.\n" \
                 "\n" \
                 "%s\n" \
                 "\n" \
                 "※ 회원님께서 위의 링크를 클릭하지 않으면 임시비밀번호는 최종 변경되지 않습니다.\n" \
                 "※ 회원님께서 재설정 요청을 하지 않은 경우 아무런 조치를 취하실 필요가 없습니다.\n" \
                 "※ 해당 메일은 답장 하실 수 없습니다. 궁금한 점이 있다면, 아래로 문의해 주시기 바랍니다.\n" \
                 "- 문의 번호 : 010-6646-5931\n" \
                 "- 문의 메일 : hd2dj07@gmail.com\n" \
                 "\n" \
                 "\n" \
                 "감사합니다\n" % (new_password, confirm_link)

    email_html = "<!DOCTYPE html><html lang='kr'><body>회원님 안녕하세요.<br />" \
                 "<br />" \
                 "비밀번호 재설정을 요청하셨습니다.<br />" \
                 "임시 비밀번호는 %s 입니다<br />" \
                 "아래의 링크를 눌러 비밀번호를 재설정하세요.<br />" \
                 "<br />" \
                 "<a href='%s' target='_blank'>비밀번호 재설정하기</a><br />" \
                 "<br />" \
                 "※ 회원님께서 위의 링크를 클릭하지 않으면 임시비밀번호는 최종 변경되지 않습니다.<br />" \
                 "※ 회원님께서 재설정 요청을 하지 않은 경우 아무런 조치를 취하실 필요가 없습니다.<br />" \
                 "※ 해당 메일은 답장 하실 수 없습니다. 궁금한 점이 있다면, 아래로 문의해 주시기 바랍니다.<br />" \
                 "- 문의 번호 : 010-6646-55931<br />" \
                 "- 문의 메일 : hd2dj07@gmail.com<br />" \
                 "<br />" \
                 "<br />" \
                 "감사합니다</body></html>" % (new_password, confirm_link)

    from_email = settings.EMAIL_HOST_USER
    send_mail("비밀번호 재설정 안내", message=email_body, html_message=email_html,
              from_email=from_email, recipient_list=[email], fail_silently=True)


def notify_security_email(email, ip_address, token, request, accesslog_pk):
    now = datetime.now()
    confirm_data = {
        'email': email,
        'date': now.isoformat(),
        'jwt': token,
        'ip_address': ip_address,
        'log': accesslog_pk
    }
    json_encoded = json.dumps(confirm_data)
    encrypted_data = aes.aes_encrypt(json_encoded)

    if "local" in get_module_config():
        domain_url = "127.0.0.1:8000"
    elif "dev" in get_module_config():
        domain_url = "radio-dev.apoweroftrance.com"
    elif "stage" in get_module_config():
        domain_url = "radio-stage.apoweroftrance.com"
    else:
        domain_url = "radio.apoweroftrance.com"

    base_url = "https://%s/v1/user/ban" % domain_url
    ban_url = "%s?auth_code=%s" % (base_url, urllib.parse.quote_plus(encrypted_data))

    base_url = "https://%s/v1/user/reset_password" % domain_url
    reset_password_url = "%s/%s" % (base_url, urllib.parse.quote_plus(email))

    email_body = "새로운 디바이스에서 계정에 로그인되었습니다. 본인이 로그인한 것이 맞나요?\n" \
                 "*위치는 로그인 IP 주소를 기준으로 한 근접한 위치입니다.\n\n" \
                 "본인이 맞는 경우,\n" \
                 "이 메시지를 무시하셔도 됩니다. 별도로 취해야 할 조치는 없습니다.\n\n" \
                 "본인이 아닌 경우,\n" \
                 "계정이 해킹되었을 수 있으며, 계정 보안을 위해 몇 가지 조치를 취해야 합니다. \n" \
                 "조치를 취해주세요 -> %s\n" \
                 "보다 안전한 조치를 위해 빠르게 임시비밀번호로 변경하시는 것이 좋습니다\n" \
                 "비밀번호 변경: %s\n" \
                 "위의 링크를 클릭하여 임시비밀번호로 변경하신 후에는 반드시 비밀번호를 원하는 비밀번호로 변경해주세요\n" \
                 "최근 6개월 이내에 사용한 이전의 비밀번호는 개인정보 보호법에 따라 재사용하실수 없습니다\n\n" \
                 "GLO에서 보낸 이메일인지 어떻게 알 수 있나요?\n" \
                 "본 이메일의 링크는 “https://”로 시작하고 “apoweroftrance.com”을 포함합니다.\n" \
                 "브라우저에 표시된 자물쇠 아이콘을 통해서도 안전한 사이트인지 확인할 수 있습니다." \
                 % (ban_url, reset_password_url)

    email_html = "<!DOCTYPE html><html lang='kr'><body>새로운 디바이스에서 계정에 로그인되었습니다. 본인이 로그인한 것이 맞나요?<br />" \
                 "*위치는 로그인 IP 주소를 기준으로 한 근접한 위치입니다.<br /><br />" \
                 "본인이 맞는 경우,<br />" \
                 "이 메시지를 무시하셔도 됩니다. 별도로 취해야 할 조치는 없습니다.<br /><br />" \
                 "본인이 아닌 경우,<br />" \
                 "계정이 해킹되었을 수 있으며, 계정 보안을 위해 몇 가지 조치를 취해야 합니다. 시작하려면 지금 비밀번호를 재설정하세요.<br />" \
                 "<a href='%s' target='_blank'>조치를 취해주세요</a><br /><br />" \
                 "보다 안전한 조치를 위해 빠르게 임시비밀번호로 변경하시는 것이 좋습니다<br />" \
                 "<a href='%s' target='_blank'>비밀번호 변경</a><br />" \
                 "위의 링크를 클릭하여 임시비밀번호로 변경하신 후에는 반드시 비밀번호를 원하는 비밀번호로 변경해주세요<br />" \
                 "최근 6개월 이내에 사용한 이전의 비밀번호는 개인정보 보호법에 따라 재사용하실수 없습니다<br /><br />" \
                 "GLO에서 보낸 이메일인지 어떻게 알 수 있나요?<br />" \
                 "본 이메일의 링크는 “https://”로 시작하고 “apoweroftrance.com”을 포함합니다.<br />" \
                 "브라우저에 표시된 자물쇠 아이콘을 통해서도 안전한 사이트인지 확인할 수 있습니다.</body></html>" \
                 % (ban_url, reset_password_url)

    from_email = settings.EMAIL_HOST_USER
    send_mail("신규 로그인 알림", message=email_body, html_message=email_html,
              from_email=from_email, recipient_list=[email], fail_silently=True)


class UpdatePUTAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    """
    Concrete view for updating a model instance.
    """
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CreateUpdateAPIView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving, updating or deleting a model instance.
    """
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CreateRetrieveAPIView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListDestroyAPIView(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving, updating or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CreateListUpdateDestroyAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving, updating or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CreateListUpdateAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving, updating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListUpdateAPIView(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for retrieving, updating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
