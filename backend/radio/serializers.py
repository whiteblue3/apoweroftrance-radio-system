from datetime import datetime
from dateutil.tz import tzlocal
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import (
    FORMAT, DEFAULT_FORMAT, CHANNEL, DEFAULT_CHANNEL,
    Track, Like, PlayHistory, PlayQueue
)


class TrackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    location = serializers.CharField(allow_null=False, allow_blank=False, max_length=255)
    format = serializers.ChoiceField(choices=FORMAT, default=DEFAULT_FORMAT, allow_null=False, allow_blank=False)
    is_service = serializers.BooleanField(default=True, allow_null=False)

    title = serializers.CharField(allow_null=False, allow_blank=False, max_length=100)
    artist = serializers.CharField(allow_null=False, allow_blank=False, max_length=30)

    description = serializers.CharField(allow_null=True, allow_blank=True)

    duration = serializers.TimeField(allow_null=False)
    play_count = serializers.IntegerField(default=0, allow_null=False)

    channel = serializers.ListField(
        child=serializers.ChoiceField(choices=CHANNEL, default=DEFAULT_CHANNEL, allow_null=False, allow_blank=False),
        allow_null=False
    )

    uploaded_at = serializers.DateTimeField(default=datetime.now(), default_timezone=tzlocal())
    last_played_at = serializers.DateTimeField(allow_null=True)

    class Meta:
        model = Track
        fields = (
            'id', 'user', 'user_id',
            'location', 'format', 'is_service',
            'title', 'artist', 'description',
            'duration', 'play_count',
            'channel', 'uploaded_at', 'last_played_at',
        )


class LikeSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    track_id = serializers.IntegerField(write_only=True)

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    like = serializers.BooleanField(default=None, allow_null=True)

    created_at = serializers.DateTimeField(default=datetime.now(), default_timezone=tzlocal())

    class Meta:
        model = Like
        fields = (
            'id', 'track', 'track_id', 'user', 'user_id',
            'like', 'created_at',
        )


class PlayHistorySerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    track_id = serializers.IntegerField(write_only=True)

    channel = serializers.ChoiceField(
        choices=CHANNEL, default=DEFAULT_CHANNEL, allow_null=False
    )

    played_at = serializers.DateTimeField(allow_null=False)

    class Meta:
        model = PlayHistory
        fields = (
            'id', 'track', 'track_id', 'channel', 'played_at',
        )


class PlayQueueSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    track_id = serializers.IntegerField(write_only=True)

    channel = serializers.ChoiceField(
        choices=CHANNEL, default=DEFAULT_CHANNEL, allow_null=False
    )

    will_play_at = serializers.DateTimeField(allow_null=True)

    class Meta:
        model = PlayQueue
        fields = (
            'id', 'track', 'track_id', 'channel', 'will_play_at',
        )

