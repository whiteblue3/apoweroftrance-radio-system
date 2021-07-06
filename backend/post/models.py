from django.db import models
from django_utils import multi_db_ralation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField


CLAIM_CATEGORY_ISSUE = "issue"
CLAIM_CATEGORY_SPAMUSER = "spamuser"
CLAIM_CATEGORY_COPYRIGHT = "copyright"

CLAIM_CATEGORY = [
    (CLAIM_CATEGORY_ISSUE, _("General Issue")),
    (CLAIM_CATEGORY_SPAMUSER, _("Spam User")),
    (CLAIM_CATEGORY_COPYRIGHT, _("Copyright Claim")),
]

CLAIM_CATEGORY_LIST = [
    CLAIM_CATEGORY_ISSUE,
    CLAIM_CATEGORY_SPAMUSER,
    CLAIM_CATEGORY_COPYRIGHT,
]

CLAIM_STATUS_OPENED = "opened"
CLAIM_STATUS_ACCEPT = "accept"
CLAIM_STATUS_CLOSED = "closed"

CLAIM_STATUS = [
    (CLAIM_STATUS_OPENED, _("Opened Issue")),
    (CLAIM_STATUS_ACCEPT, _("Accepted")),
    (CLAIM_STATUS_CLOSED, _("Closed Issue")),
]

CLAIM_STATUS_LIST = [
    CLAIM_STATUS_OPENED,
    CLAIM_STATUS_ACCEPT,
    CLAIM_STATUS_CLOSED,
]

CLAIM_STAFF_ACTION_NOACTION = "noaction"
CLAIM_STAFF_ACTION_APPROVED = "approved"
CLAIM_STAFF_ACTION_HOLD = "hold"

CLAIM_STAFF_ACTION = [
    (CLAIM_STAFF_ACTION_NOACTION, _("No Action")),
    (CLAIM_STAFF_ACTION_APPROVED, _("Approved")),
    (CLAIM_STAFF_ACTION_HOLD, _("Hold")),
]

CLAIM_STAFF_ACTION_LIST = [
    CLAIM_STAFF_ACTION_NOACTION,
    CLAIM_STAFF_ACTION_APPROVED,
    CLAIM_STAFF_ACTION_HOLD,
]

NOTIFICATION_CATEGORY_NOTIFICATION = "notification"
NOTIFICATION_CATEGORY_CLAIMUSER = "claim_user"
NOTIFICATION_CATEGORY_CLAIMCOPYRIGHT = "claim_copyright"

NOTIFICATION_CATEGORY = [
    (NOTIFICATION_CATEGORY_NOTIFICATION, _("Notification")),
    (NOTIFICATION_CATEGORY_CLAIMUSER, _("User Claim")),
    (NOTIFICATION_CATEGORY_CLAIMCOPYRIGHT, _("Copyright Claim")),
]

NOTIFICATION_CATEGORY_LIST = [
    NOTIFICATION_CATEGORY_NOTIFICATION,
    NOTIFICATION_CATEGORY_CLAIMUSER,
    NOTIFICATION_CATEGORY_CLAIMCOPYRIGHT,
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

    category = models.CharField(choices=CLAIM_CATEGORY, default=CLAIM_CATEGORY_ISSUE, null=False, blank=False, max_length=20)

    user = models.ForeignKey(
        get_user_model(), related_name='Claim.user+', on_delete=models.CASCADE, null=True, blank=True
    )

    track = models.ForeignKey(
        'radio.Track', related_name='Claim.track+', on_delete=models.CASCADE, null=True, blank=True
    )

    issue = models.CharField(blank=True, null=True, max_length=150)
    reason = models.TextField(blank=False, null=False)

    status = models.CharField(choices=CLAIM_STATUS, default=CLAIM_STATUS_OPENED, null=False, blank=False, max_length=20)
    staff_action = models.CharField(choices=CLAIM_STAFF_ACTION, default=CLAIM_STAFF_ACTION_NOACTION, null=False, blank=False, max_length=20)

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
        external_db_fields = ['claim', 'user']
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


class TrackTag(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    track = models.ForeignKey(
        'radio.Track', on_delete=models.CASCADE, null=False, blank=False
    )

    tag = models.CharField(blank=False, null=False, max_length=150)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'post'
        external_db_fields = ['track']
        verbose_name = 'TrackTag'
        verbose_name_plural = 'TrackTag'
