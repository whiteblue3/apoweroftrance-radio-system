# import os
import json
import secrets
import smtplib
from datetime import datetime, timedelta
import urllib.parse
# from django.core.mail import send_mail
# from django.core.mail import EmailMessage
from django.conf import settings
from .serializers import (
    AccessLogSerializer
)
from .models import Profile
from .access_log import *
from .error import ProfileDoesNotExist
from django_utils import aes, storage


if settings.DOMAIN_URL is None:
    domain_url = "127.0.0.1:8080"
else:
    domain_url = settings.AUTH_DOMAIN_URL

if settings.WWW_LANDING_URL is None:
    www_landing_url = "127.0.0.1:8081"
else:
    www_landing_url = settings.WWW_LANDING_URL

if settings.ACCOUNT_API_PATH is None:
    user_api_path = "/v1/user"
else:
    user_api_path = settings.ACCOUNT_API_PATH

if settings.ACCOUNT_LANDING_PATH is None:
    account_landing_path = "/v1/user"
else:
    account_landing_path = settings.ACCOUNT_LANDING_PATH

# Activate Account Email
if settings.ACTIVATE_ACCOUNT_EMAIL_TITLE is None:
    activate_account_email_title = "회원가입 이메일 인증 안내"
else:
    activate_account_email_title = settings.ACTIVATE_ACCOUNT_EMAIL_TITLE

if settings.ACTIVATE_ACCOUNT_EMAIL_BODY is None:
    activate_account_email_body = "안녕하세요.\n" \
                                  "\n" \
                                  "회원이 되신 것을 진심으로 축하드립니다\n" \
                                  "아래 링크를 클릭하면 회원가입 인증이 완료됩니다\n" \
                                  "\n" \
                                  "%s\n" \
                                  "\n" \
                                  "감사합니다\n"
else:
    activate_account_email_body = settings.ACTIVATE_ACCOUNT_EMAIL_BODY

if settings.ACTIVATE_ACCOUNT_EMAIL_HTML is None:
    activate_account_email_html = "<!DOCTYPE html><html lang='kr'><body>안녕하세요.<br />" \
                                  "<br />" \
                                  "회원이 되신 것을 진심으로 축하드립니다<br />" \
                                  "아래 링크를 클릭하면 회원가입 인증이 완료됩니다<br />" \
                                  "<br />" \
                                  "<a href='%s' target='_blank'>회원가입 완료하기</a><br />" \
                                  "감사합니다</body></html>"
else:
    activate_account_email_html = settings.ACTIVATE_ACCOUNT_EMAIL_HTML

# Reset Password Email
if settings.RESET_PASSWORD_EMAIL_TITLE is None:
    reset_password_email_title = "비밀번호 재설정"
else:
    reset_password_email_title = settings.RESET_PASSWORD_EMAIL_TITLE

if settings.RESET_PASSWORD_EMAIL_BODY is None:
    reset_password_email_body = "임시 비밀번호: %s\n" \
                                "비밀번호 재설정하기: %s\n"
else:
    reset_password_email_body = settings.RESET_PASSWORD_EMAIL_BODY

if settings.RESET_PASSWORD_EMAIL_HTML is None:
    reset_password_email_html = "<!DOCTYPE html><html lang='kr'><body>" \
                                "임시 비밀번호: %s<br />" \
                                "<a href='%s' target='_blank'>비밀번호 재설정하기</a><br />" \
                                "</body></html>"
else:
    reset_password_email_html = settings.RESET_PASSWORD_EMAIL_HTML

# Notify Security Alert Email
if settings.NOTIFY_SECURITY_ALERT_EMAIL_TITLE is None:
    notify_security_alert_email_title = "신규 로그인 알림"
else:
    notify_security_alert_email_title = settings.NOTIFY_SECURITY_ALERT_EMAIL_TITLE

if settings.NOTIFY_SECURITY_ALERT_EMAIL_BODY is None:
    notify_security_alert_email_body = "새로운 디바이스에서 계정에 로그인되었습니다. 본인이 로그인한 것이 맞나요?\n" \
                                       "본인이 맞는 경우,\n" \
                                       "이 메시지를 무시하셔도 됩니다. 별도로 취해야 할 조치는 없습니다.\n\n" \
                                       "본인이 아닌 경우,\n" \
                                       "계정이 해킹되었을 수 있으며, 계정 보안을 위해 몇 가지 조치를 취해야 합니다. \n" \
                                       "조치를 취해주세요 -> %s\n" \
                                       "보다 안전한 조치를 위해 빠르게 임시비밀번호로 변경하시는 것이 좋습니다\n" \
                                       "비밀번호 변경: %s\n" \
                                       "위의 링크를 클릭하여 임시비밀번호로 변경하신 후에는 반드시 비밀번호를 원하는 비밀번호로 변경해주세요\n"
else:
    notify_security_alert_email_body = settings.NOTIFY_SECURITY_ALERT_EMAIL_BODY

if settings.NOTIFY_SECURITY_ALERT_EMAIL_HTML is None:
    notify_security_alert_email_html = "<!DOCTYPE html><html lang='kr'><body>" \
                                       "새로운 디바이스에서 계정에 로그인되었습니다. 본인이 로그인한 것이 맞나요?<br />" \
                                       "본인이 맞는 경우,<br />" \
                                       "이 메시지를 무시하셔도 됩니다. 별도로 취해야 할 조치는 없습니다.<br /><br />" \
                                       "본인이 아닌 경우,<br />" \
                                       "계정이 해킹되었을 수 있으며, 계정 보안을 위해 몇 가지 조치를 취해야 합니다. " \
                                       "시작하려면 지금 비밀번호를 재설정하세요.<br />" \
                                       "<a href='%s' target='_blank'>조치를 취해주세요</a><br /><br />" \
                                       "보다 안전한 조치를 위해 빠르게 임시비밀번호로 변경하시는 것이 좋습니다<br />" \
                                       "<a href='%s' target='_blank'>비밀번호 변경</a><br />" \
                                       "</body></html>"
else:
    notify_security_alert_email_html = settings.NOTIFY_SECURITY_ALERT_EMAIL_HTML


def accesslog(request, access_type, status, email, ip):
    data = {
        'email': email,
        'ip_address': ip,
        'request': '%s %s' % (request.method, request.get_full_path()),
        'access_type': access_type,
        'access_status': status
    }

    if hasattr(request, 'data'):
        data['request_body'] = str(request.data)
    else:
        data['request_body'] = None

    """Remove authenticate information for security"""
    if access_type is ACCESS_TYPE_AUTHENTICATE:
        data.pop('request_body')
    elif access_type is ACCESS_TYPE_BAN:
        data['request'] = '%s %s' % (request.method, request.path)
        data['request_body'] = 'auth_code=%s' % (request.GET.get('auth_code'))

    accesslog_serializer = AccessLogSerializer(data=data)
    accesslog_serializer.is_valid(raise_exception=True)
    accesslog_serializer.save()


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


def upload_profile_image(email, request, fuse):
    profile = get_profile(email)

    # Store previous image file name
    prev_image = profile.image

    storage_driver = fuse

    # Upload file if file given
    try:
        filepath = storage.upload_file(request, 'image', 'image', storage_driver, ["image/png", "image/jpeg"])
        if filepath is not None:
            image_path = filepath[0]
            profile.image = image_path
            profile.save()
    except Exception as e:
        raise e

    # Delete previous image file if new image file has been uploaded successful
    try:
        if filepath is not None:
            if storage.exist_file('image', prev_image, storage_driver):
                storage.delete_file('image', prev_image, storage_driver)
    except Exception as e:
        # 파일이 존재하지 않는 경우 이곳으로 온다
        pass


def get_domain():
    return settings.DOMAIN_URL


def generate_password(length=11, charset="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()"):
    return "".join([secrets.choice(charset) for _ in range(0, length)])


def send_account_activation_email(email):
    # send email
    now = datetime.utcnow()
    expire = (now + timedelta(minutes=30))
    confirm_data = {
        'email': email,
        'date': now.isoformat(),
        'expire': expire.isoformat()
    }
    json_encoded = json.dumps(confirm_data)
    encrypted_data = aes.aes_encrypt(json_encoded)

    base_url = "%s://%s%s/activate" % (settings.HTTP_PROTOCOL, www_landing_url, account_landing_path)
    confirm_link = "%s?auth_code=%s" % (base_url, urllib.parse.quote_plus(encrypted_data))

    email_body = activate_account_email_body % confirm_link
    email_html = activate_account_email_html % confirm_link

    from_email = settings.EMAIL_HOST_USER
    # send_mail(activate_account_email_title, message=email_body, html_message=email_html,
    #           from_email=from_email, recipient_list=[email], fail_silently=True)

    # https://medium.com/@mika94322/python-smtp-email-%EC%A0%84%EC%86%A1-%EC%98%88%EC%A0%9C-c7e6e095dcfc
    server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    BODY = '\r\n'.join(['To: %s' % email,
                        'From: %s' % from_email,
                        'Subject: %s' % activate_account_email_title,
                        '', email_body])

    server.sendmail(settings.EMAIL_HOST_USER, [email], BODY.encode('utf-8'))

    # msg = EmailMessage(activate_account_email_title,
    #                    email_body, from_email=from_email, to=[email])
    # msg.send()

    server.quit()


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

    base_url = "%s://%s%s/confirm_reset_password" % (settings.HTTP_PROTOCOL, www_landing_url, account_landing_path)
    confirm_link = "%s?auth_code=%s" % (base_url, urllib.parse.quote_plus(encrypted_data))

    email_body = reset_password_email_body % (new_password, confirm_link)
    email_html = reset_password_email_html % (new_password, confirm_link)

    from_email = settings.EMAIL_HOST_USER
    # send_mail(reset_password_email_title, message=email_body, html_message=email_html,
    #           from_email=from_email, recipient_list=[email], fail_silently=True)

    server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    BODY = '\r\n'.join(['To: %s' % email,
                        'From: %s' % from_email,
                        'Subject: %s' % reset_password_email_title,
                        '', email_body])

    server.sendmail(settings.EMAIL_HOST_USER, [email], BODY.encode('utf-8'))

    # msg = EmailMessage(reset_password_email_title,
    #                    email_body, from_email=from_email, to=[email])
    # msg.send()

    server.quit()


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

    base_url = "%s://%s%s/ban" % (settings.HTTP_PROTOCOL, www_landing_url, account_landing_path)
    ban_url = "%s?auth_code=%s" % (base_url, urllib.parse.quote_plus(encrypted_data))

    base_url = "%s://%s%s/reset_password" % (settings.HTTP_PROTOCOL, www_landing_url, account_landing_path)
    reset_password_url = "%s/%s" % (base_url, urllib.parse.quote_plus(email))

    email_body = notify_security_alert_email_body % (ban_url, reset_password_url)
    email_html = notify_security_alert_email_html % (ban_url, reset_password_url)

    from_email = settings.EMAIL_HOST_USER
    # send_mail(notify_security_alert_email_title, message=email_body, html_message=email_html,
    #           from_email=from_email, recipient_list=[email], fail_silently=True)

    server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    BODY = '\r\n'.join(['To: %s' % email,
                        'From: %s' % from_email,
                        'Subject: %s' % notify_security_alert_email_title,
                        '', email_body])

    server.sendmail(settings.EMAIL_HOST_USER, [email], BODY.encode('utf-8'))

    # msg = EmailMessage(notify_security_alert_email_title,
    #                    email_body, from_email=from_email, to=[email])
    # msg.send()

    server.quit()
