from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _


CHANNEL = [
    ("yui", _("YUI")),
    # ("alice", _("ALICE")),
    # ("miku", _("MIKU")),
]
DEFAULT_CHANNEL = "yui"
SERVICE_CHANNEL = [
    "yui"
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


class Track(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False
    )

    location = models.FilePathField(null=False, blank=False)
    format = models.CharField(choices=FORMAT, default=DEFAULT_FORMAT, null=False, blank=False, max_length=3)
    is_service = models.BooleanField(default=True, null=False, blank=False)

    title = models.CharField(null=False, blank=False, max_length=100)
    artist = models.CharField(null=False, blank=False, max_length=30)

    description = models.TextField(null=True, blank=True)

    duration = models.TimeField(null=False, blank=False)
    play_count = models.PositiveIntegerField(default=0, null=False)

    channel = ArrayField(
        models.CharField(choices=CHANNEL, default=DEFAULT_CHANNEL, null=False, blank=False, max_length=15),
        null=False, blank=False
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_played_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Music'
        verbose_name_plural = 'Music'

    def __str__(self):
        return "%s - %s" % (self.artist, self.title)


class Like(models.Model):
    track = models.ForeignKey(
        'radio.Track', on_delete=models.CASCADE, null=False, blank=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False
    )

    like = models.BooleanField(default=None, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Like'


class PlayHistory(models.Model):
    track = models.ForeignKey(
        'radio.Track', on_delete=models.CASCADE, null=False, blank=False
    )

    channel = models.CharField(choices=CHANNEL, default=DEFAULT_CHANNEL, null=False, blank=False, max_length=15)

    played_at = models.DateTimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'Play History'
        verbose_name_plural = 'Play History'


class PlayQueue(models.Model):
    track = models.ForeignKey(
        'radio.Track', on_delete=models.CASCADE, null=False, blank=False
    )

    channel = models.CharField(choices=CHANNEL, default=DEFAULT_CHANNEL, null=False, blank=False, max_length=15)

    will_play_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Play List'
        verbose_name_plural = 'Play List'
