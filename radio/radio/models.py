from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_utils import multi_db_ralation


CHANNEL = [
    ("yui", _("YUI")),
    ("alice", _("ALICE")),
    ("miku", _("MIKU")),
    ("lena", _("LENA")),
]
DEFAULT_CHANNEL = "yui"
SERVICE_CHANNEL = [
    "yui",
    "alice",
    "miku",
    "lena",
]

FORMAT_MP3 = "mp3"
FORMAT_M4A = "m4a"
FORMAT = [
    (FORMAT_MP3, _("MP3")),
    # (FORMAT_M4A, _("M4A")),
]
DEFAULT_FORMAT = FORMAT_MP3
SUPPORT_FORMAT = [
    FORMAT_MP3,
    # FORMAT_M4A
]


class ModelQuerySet(multi_db_ralation.ExternalDbQuerySetMixin, models.QuerySet):
    pass


class Track(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False, editable=False
    )

    location = models.CharField(null=False, blank=False, max_length=254)
    format = models.CharField(choices=FORMAT, default=DEFAULT_FORMAT, null=False, blank=False, max_length=3)
    is_service = models.BooleanField(default=True, null=False, blank=False)
    cover_art = models.CharField(null=True, blank=True, max_length=254)

    title = models.CharField(null=False, blank=False, max_length=200)
    artist = models.CharField(null=False, blank=False, max_length=70)

    description = models.TextField(null=True, blank=True)

    bpm = models.FloatField(null=True, blank=True, default=None)
    scale = models.CharField(null=True, blank=True, max_length=15, default=None)

    queue_in = models.TimeField(null=True, blank=True, default=None)
    queue_out = models.TimeField(null=True, blank=True, default=None)
    mix_in = models.TimeField(null=True, blank=True, default=None)
    mix_out = models.TimeField(null=True, blank=True, default=None)
    ment_in = models.TimeField(null=True, blank=True, default=None)

    duration = models.TimeField(null=False, blank=False)
    play_count = models.PositiveIntegerField(default=0, null=False, editable=False)
    listen_count = models.PositiveIntegerField(default=0, null=False, editable=False)

    channel = ArrayField(
        models.CharField(choices=CHANNEL, default=DEFAULT_CHANNEL, null=False, blank=False, max_length=15),
        null=False, blank=False, editable=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    last_played_at = models.DateTimeField(null=True, blank=True, editable=False)

    is_ban = models.BooleanField(default=False, null=False, blank=False)
    ban_reason = models.TextField(null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0, null=False, editable=False)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'radio'
        external_db_fields = ['user']
        verbose_name = 'Music'
        verbose_name_plural = 'Music'

    def __str__(self):
        return "%s - %s" % (self.artist, self.title)


class Like(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    track = models.ForeignKey(
        'radio.Track', on_delete=models.CASCADE, null=False, blank=False, editable=False
    )

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False, editable=False
    )

    like = models.BooleanField(default=False, null=False, blank=False)

    updated_at = models.DateTimeField(auto_now_add=True, editable=False)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'radio'
        external_db_fields = ['user']
        verbose_name = 'Like'
        verbose_name_plural = 'Like'


class PlayHistory(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    track = models.ForeignKey(
        'radio.Track', on_delete=models.SET_NULL, null=True, editable=False
    )

    title = models.CharField(null=True, blank=True, max_length=200, editable=False)
    artist = models.CharField(null=True, blank=True, max_length=70, editable=False)

    channel = models.CharField(
        choices=CHANNEL, default=DEFAULT_CHANNEL, null=False, blank=False, max_length=15, editable=False
    )

    played_at = models.DateTimeField(null=False, blank=False, editable=False)

    class Meta:
        app_label = 'radio'
        verbose_name = 'Play History'
        verbose_name_plural = 'Play History'


class ListenHistory(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False, editable=False
    )

    track = models.ForeignKey(
        'radio.Track', on_delete=models.SET_NULL, null=True, editable=False
    )

    title = models.CharField(null=True, blank=True, max_length=200, editable=False)
    artist = models.CharField(null=True, blank=True, max_length=70, editable=False)

    played_at = models.DateTimeField(null=False, blank=False, editable=False)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'radio'
        verbose_name = 'Listen History'
        verbose_name_plural = 'Listen History'
