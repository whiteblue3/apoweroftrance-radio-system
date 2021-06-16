from django.db import models
from django_utils import multi_db_ralation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model


CLAIM_CATEGORY = [
    ("spamuser", _("Spam User")),
    ("copyright", _("Copyright Claim")),
]

CLAIM_STATUS = [
    ("opened", _("Opened Issue")),
    ("accept", _("Accepted")),
    ("closed", _("Closed Issue")),
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

    category = models.CharField(choices=CLAIM_CATEGORY, null=False, blank=False, max_length=20)

    user = models.ForeignKey(
        get_user_model(), related_name='Claim.user+', on_delete=models.CASCADE, null=True, blank=True
    )

    track = models.ForeignKey(
        'radio.Track', related_name='Claim.track+', on_delete=models.CASCADE, null=True, blank=True
    )

    issue = models.CharField(blank=True, null=True, max_length=150)
    reason = models.TextField(blank=False, null=False)

    status = models.CharField(choices=CLAIM_STATUS, null=False, blank=False, max_length=20)

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
