import smtplib
from datetime import datetime
from dateutil.tz import tzlocal
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from .models import (
    Notification, NOTIFICATION_CATEGORY_LIST
)


# Claim User Email
if settings.CLAIM_USER_EMAIL_TITLE is None:
    claim_user_email_title = "클레임으로 인한 계정 제한 안내"
else:
    claim_user_email_title = settings.CLAIM_USER_EMAIL_TITLE

if settings.CLAIM_USER_EMAIL_BODY is None:
    claim_user_email_body = "안녕하세요. A Power of Trance 입니다\n" \
                              "\n" \
                              "클레임이 접수되어 계정에 제한이 이루어졌습니다\n" \
                              "제한되는 기능은 아래와 같습니다\n" \
                              "- 트랙 업로드\n" \
                              "- 댓글 달기\n" \
                              "\n" \
                              "감사합니다\n"
else:
    claim_user_email_body = settings.CLAIM_USER_EMAIL_BODY

if settings.CLAIM_USER_EMAIL_HTML is None:
    claim_user_email_html = "<!DOCTYPE html><html lang='kr'><body>안녕하세요. A Power of Trance 입니다<br />" \
                              "<br />" \
                              "클레임이 접수되어 계정에 제한이 이루어졌습니다<br />" \
                              "제한되는 기능은 아래와 같습니다<br />" \
                              "- 트랙 업로드<br />" \
                              "- 댓글 달기<br />" \
                              "<br />" \
                              "감사합니다</body></html>"
else:
    claim_user_email_html = settings.CLAIM_USER_EMAIL_HTML


# Claim Copyright Email
if settings.CLAIM_COPYRIGHT_EMAIL_TITLE is None:
    claim_copyright_email_title = "저작권법 위반 안내"
else:
    claim_copyright_email_title = settings.CLAIM_COPYRIGHT_EMAIL_TITLE

if settings.CLAIM_COPYRIGHT_EMAIL_BODY is None:
    claim_copyright_email_body = "안녕하세요. A Power of Trance 입니다\n" \
                              "\n" \
                              "클레임이 접수되어 계정에 제한이 이루어졌습니다\n" \
                              "제한되는 기능은 아래와 같습니다\n" \
                              "- 트랙 업로드\n" \
                              "- 댓글 달기\n" \
                              "\n" \
                              "감사합니다\n"
else:
    claim_copyright_email_body = settings.CLAIM_COPYRIGHT_EMAIL_BODY

if settings.CLAIM_COPYRIGHT_EMAIL_HTML is None:
    claim_copyright_email_html = "<!DOCTYPE html><html lang='kr'><body>안녕하세요. A Power of Trance 입니다<br />" \
                              "<br />" \
                              "클레임이 접수되어 계정에 제한이 이루어졌습니다<br />" \
                              "제한되는 기능은 아래와 같습니다<br />" \
                              "- 트랙 업로드<br />" \
                              "- 댓글 달기<br />" \
                              "<br />" \
                              "감사합니다</body></html>"
else:
    claim_copyright_email_html = settings.CLAIM_COPYRIGHT_EMAIL_HTML


def now():
    return str(datetime.now(tz=tzlocal()).isoformat())


def send_notification(category, title, message, target=None, extra=None):
    if category not in NOTIFICATION_CATEGORY_LIST:
        raise ValidationError(_("Invalid category"))

    record = Notification(
        category=category,
        title=title,
        message=message
    )

    if extra is not None:
        record.data = extra

    record.save()

    if target is not None:
        if isinstance(target, list) is False:
            raise ValidationError(_("Invalid target"))

        for user_id in target:
            try:
                User = get_user_model()
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError(_("User does not exist"))

            record.targets.add(target_user)


def send_email_claim_spamuser(email):
    email_body = claim_user_email_body
    email_html = claim_user_email_html

    from_email = settings.EMAIL_HOST_USER
    # send_mail(notify_security_alert_email_title, message=email_body, html_message=email_html,
    #           from_email=from_email, recipient_list=[email], fail_silently=True)

    server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    BODY = '\r\n'.join(['To: %s' % email,
                        'From: %s' % from_email,
                        'Subject: %s' % claim_user_email_title,
                        '', email_body])

    server.sendmail(settings.EMAIL_HOST_USER, [email], BODY.encode('utf-8'))

    # msg = EmailMessage(notify_security_alert_email_title,
    #                    email_body, from_email=from_email, to=[email])
    # msg.send()

    server.quit()


def send_email_claim_copyright(email, track):
    track_title = "%s - %s" % (track.artist, track.title)
    email_body = claim_copyright_email_body % track_title
    email_html = claim_copyright_email_html % track_title

    from_email = settings.EMAIL_HOST_USER
    # send_mail(notify_security_alert_email_title, message=email_body, html_message=email_html,
    #           from_email=from_email, recipient_list=[email], fail_silently=True)

    server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    BODY = '\r\n'.join(['To: %s' % email,
                        'From: %s' % from_email,
                        'Subject: %s' % claim_copyright_email_title,
                        '', email_body])

    server.sendmail(settings.EMAIL_HOST_USER, [email], BODY.encode('utf-8'))

    # msg = EmailMessage(notify_security_alert_email_title,
    #                    email_body, from_email=from_email, to=[email])
    # msg.send()

    server.quit()
