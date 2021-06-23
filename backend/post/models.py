from django.db import models
from django_utils import multi_db_ralation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField


CLAIM_CATEGORY = [
    ("issue", _("General Issue")),
    ("spamuser", _("Spam User")),
    ("copyright", _("Copyright Claim")),
]

CLAIM_STATUS = [
    ("opened", _("Opened Issue")),
    ("accept", _("Accepted")),
    ("closed", _("Closed Issue")),
]

CLAIM_STAFF_ACTION = [
    ("noaction", _("No Action")),
    ("approved", _("Approved")),
    ("hold", _("Hold")),
]

NOTIFICATION_CATEGORY = [
    ("notification", _("Notification")),
    ("claim_user", _("User Claim")),
    ("claim_copyright", _("Copyright Claim")),
]

NOTIFICATION_CATEGORY_LIST = [
    "notification",
    "claim_user",
    "claim_copyright",
]


class ModelQuerySet(multi_db_ralation.ExternalDbQuerySetMixin, models.QuerySet):
    pass


class Claim(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    issuer = models.ForeignKey(
        get_user_model(), related_name='Claim.issuer+', on_delete=models.CASCADE, null=False, blank=False
    )

    accepter = models.ForeignKey(
        get_user_model(), related_name='Claim.accepter+', on_delete=models.CASCADE, null=True, blank=True
    )

    category = models.CharField(choices=CLAIM_CATEGORY, default="issue", null=False, blank=False, max_length=20)

    user = models.ForeignKey(
        get_user_model(), related_name='Claim.user+', on_delete=models.CASCADE, null=True, blank=True
    )

    track = models.ForeignKey(
        'radio.Track', related_name='Claim.track+', on_delete=models.CASCADE, null=True, blank=True
    )

    issue = models.CharField(blank=True, null=True, max_length=150)
    reason = models.TextField(blank=False, null=False)

    status = models.CharField(choices=CLAIM_STATUS, default="opened", null=False, blank=False, max_length=20)
    staff_action = models.CharField(choices=CLAIM_STAFF_ACTION, default="noaction", null=False, blank=False, max_length=20)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'post'
        external_db_fields = ['issuer', 'accepter', 'user', 'track']
        verbose_name = 'Claim'
        verbose_name_plural = 'Claim'


class ClaimReply(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    claim = models.ForeignKey(
        'post.Claim', on_delete=models.CASCADE, null=False, blank=False
    )

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False
    )

    message = models.TextField(blank=False, null=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'post'
        external_db_fields = ['user']
        verbose_name = 'ClaimReply'
        verbose_name_plural = 'ClaimReply'


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False
    )

    track = models.ForeignKey(
        'radio.Track', on_delete=models.CASCADE, null=False, blank=False
    )

    message = models.TextField(blank=False, null=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'post'
        external_db_fields = ['user', 'track']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comment'


class DirectMessage(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    send_user = models.ForeignKey(
        get_user_model(), related_name='DirectMessage.send_user+', on_delete=models.CASCADE, null=False, blank=False
    )

    target_user = models.ForeignKey(
        get_user_model(), related_name='DirectMessage.target_user+', on_delete=models.CASCADE, null=False, blank=False
    )

    message = models.TextField(blank=False, null=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'post'
        external_db_fields = ['send_user', 'target_user']
        verbose_name = 'DirectMessage'
        verbose_name_plural = 'DirectMessage'


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    category = models.CharField(choices=NOTIFICATION_CATEGORY, null=False, blank=False, max_length=20)

    targets = models.ManyToManyField(get_user_model(), blank=True, through='NotificationUser')

    title = models.CharField(blank=False, null=False, max_length=150)
    message = models.TextField(blank=False, null=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'post'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notification'


class NotificationUser(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        db_table = 'post_notification_targets'
