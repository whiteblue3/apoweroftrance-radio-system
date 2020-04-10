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

FORMAT = [
    ("mp3", _("MP3")),
    # ("aac", _("AAC")),
]
DEFAULT_FORMAT = "mp3"


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
        verbose_name = '음원'
        verbose_name_plural = '음원'

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
        verbose_name = '좋아요'
        verbose_name_plural = '좋아요'


class PlayHistory(models.Model):
    track = models.ForeignKey(
        'radio.Track', on_delete=models.CASCADE, null=False, blank=False
    )

    channel = models.CharField(choices=CHANNEL, default=DEFAULT_CHANNEL, null=False, blank=False, max_length=15)

    played_at = models.DateTimeField(null=False, blank=False)

    class Meta:
        verbose_name = '송출 이력'
        verbose_name_plural = '송출 이력'


class PlayQueue(models.Model):
    track = models.ForeignKey(
        'radio.Track', on_delete=models.CASCADE, null=False, blank=False
    )

    channel = models.CharField(choices=CHANNEL, default=DEFAULT_CHANNEL, null=False, blank=False, max_length=15)

    will_play_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = '편성표'
        verbose_name_plural = '편성표'
