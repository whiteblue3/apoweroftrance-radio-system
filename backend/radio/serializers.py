from datetime import datetime
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import (
    FORMAT, DEFAULT_FORMAT, CHANNEL, DEFAULT_CHANNEL,
    Track, Like, PlayHistory, PlayQueue
)


class TrackSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    location = serializers.FilePathField(allow_null=False, allow_blank=False)
    format = serializers.ChoiceField(choices=FORMAT, default=DEFAULT_FORMAT, allow_null=False, allow_blank=False)

    title = serializers.CharField(allow_null=False, allow_blank=False, max_length=100)
    artist = serializers.CharField(allow_null=False, allow_blank=False, max_length=30)

    description = serializers.CharField(allow_null=True, allow_blank=True)

    duration = serializers.TimeField(allow_null=False, allow_blank=False)
    play_count = serializers.IntegerField(default=0, allow_null=False)

    channel = serializers.ListField(
        child=serializers.ChoiceField(choices=CHANNEL, default=DEFAULT_CHANNEL, null=False, blank=False),
        allow_null=False, allow_blank=False
    )

    uploaded_at = serializers.DateTimeField(default=datetime.now(), default_timezone="Asia/Seoul")
    last_played_at = serializers.DateTimeField(allow_null=True, allow_blank=True)

    class Meta:
        model = Track
        fields = (
            'id', 'user',
            'location', 'format',
            'title', 'artist', 'description',
            'duration', 'play_count',
            'channel', 'uploaded_at', 'last_played_at',
        )


class LikeSerializer(serializers.ModelSerializer):
    track = TrackSerializer()

    user = UserSerializer()

    like = serializers.BooleanField(default=None, allow_null=True, allow_blank=True)

    created_at = serializers.DateTimeField(default=datetime.now(), default_timezone="Asia/Seoul")

    class Meta:
        model = Like
        fields = (
            'id', 'track', 'user',
            'like', 'created_at',
        )


class PlayHistorySerializer(serializers.ModelSerializer):
    track = TrackSerializer()

    channel = serializers.ChoiceField(
        choices=CHANNEL, default=DEFAULT_CHANNEL, allow_null=False, allow_blank=False, max_length=15
    )

    played_at = serializers.DateTimeField(allow_null=False, allow_blank=False)

    class Meta:
        model = PlayHistory
        fields = (
            'id', 'track', 'channel', 'played_at',
        )


class PlayQueueSerializer(serializers.ModelSerializer):
    track = TrackSerializer()

    channel = serializers.ChoiceField(
        choices=CHANNEL, default=DEFAULT_CHANNEL, allow_null=False, allow_blank=False, max_length=15
    )

    will_play_at = serializers.DateTimeField(allow_null=True, allow_blank=True)

    class Meta:
        model = PlayQueue
        fields = (
            'id', 'track', 'channel', 'will_play_at',
        )

