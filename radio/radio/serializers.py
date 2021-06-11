from datetime import datetime
from dateutil.tz import tzlocal
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import (
    FORMAT, DEFAULT_FORMAT, CHANNEL, DEFAULT_CHANNEL,
    Track, Like, PlayHistory
)


class TrackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    location = serializers.CharField(allow_null=False, allow_blank=False, max_length=255)
    format = serializers.ChoiceField(choices=FORMAT, default=DEFAULT_FORMAT, allow_null=False, allow_blank=False)
    is_service = serializers.BooleanField(default=True, allow_null=False)
    cover_art = serializers.CharField(allow_null=True, allow_blank=True, max_length=255)

    title = serializers.CharField(allow_null=False, allow_blank=False, max_length=200)
    artist = serializers.CharField(allow_null=False, allow_blank=False, max_length=70)

    description = serializers.CharField(allow_null=True, allow_blank=True)

    bpm = serializers.FloatField(allow_null=True, default=None)
    scale = serializers.CharField(allow_null=True, default=None, max_length=15)

    queue_in = serializers.TimeField(allow_null=True, default=None)
    queue_out = serializers.TimeField(allow_null=True, default=None)
    mix_in = serializers.TimeField(allow_null=True, default=None)
    mix_out = serializers.TimeField(allow_null=True, default=None)
    ment_in = serializers.TimeField(allow_null=True, default=None)

    duration = serializers.TimeField(allow_null=False)
    play_count = serializers.IntegerField(default=0, allow_null=False)

    channel = serializers.ListField(
        child=serializers.ChoiceField(choices=CHANNEL, default=DEFAULT_CHANNEL, allow_null=False, allow_blank=False),
        allow_null=False
    )

    uploaded_at = serializers.DateTimeField(default=datetime.now(), default_timezone=tzlocal())
    updated_at = serializers.DateTimeField(default=datetime.now(), default_timezone=tzlocal())
    last_played_at = serializers.DateTimeField(allow_null=True)

    is_ban = serializers.BooleanField(default=False, allow_null=False)
    ban_reason = serializers.CharField(allow_null=True, allow_blank=True)
    like_count = serializers.IntegerField(default=0, allow_null=False)

    class Meta:
        model = Track
        fields = (
            'id', 'user', 'user_id',
            'location', 'format', 'is_service', 'cover_art',
            'title', 'artist', 'description',
            'bpm', 'scale',
            'queue_in', 'queue_out', 'mix_in', 'mix_out', 'ment_in',
            'duration', 'play_count', 'like_count',
            'channel', 'uploaded_at', 'updated_at', 'last_played_at',
            'is_ban', 'ban_reason',
        )


class TrackAPISerializer(serializers.Serializer):
    is_service = serializers.BooleanField(default=True, allow_null=False)
    cover_art = serializers.CharField(allow_null=True, allow_blank=True, max_length=255)

    title = serializers.CharField(allow_null=False, allow_blank=False, max_length=200)
    artist = serializers.CharField(allow_null=False, allow_blank=False, max_length=70)

    description = serializers.CharField(allow_null=True, allow_blank=True)

    bpm = serializers.FloatField(allow_null=True, default=None)
    scale = serializers.CharField(allow_null=True, default=None, max_length=15)

    queue_in = serializers.TimeField(allow_null=True, default=None)
    queue_out = serializers.TimeField(allow_null=True, default=None)
    mix_in = serializers.TimeField(allow_null=True, default=None)
    mix_out = serializers.TimeField(allow_null=True, default=None)
    ment_in = serializers.TimeField(allow_null=True, default=None)

    channel = serializers.ListField(
        child=serializers.ChoiceField(choices=CHANNEL, default=DEFAULT_CHANNEL, allow_null=False, allow_blank=False),
        allow_null=False
    )

    class Meta:
        model = Track
        fields = (
            'is_service', 'cover_art',
            'title', 'artist', 'description',
            'bpm', 'scale',
            'queue_in', 'queue_out', 'mix_in', 'mix_out', 'ment_in',
            'channel',
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
        # for (key, value) in validated_data.items():
        #     setattr(instance, key, value)
        #
        # instance.save()
        #
        # return instance


class LikeSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    track_id = serializers.IntegerField(write_only=True)

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    like = serializers.BooleanField(default=False, allow_null=False)

    updated_at = serializers.DateTimeField(default=datetime.now(), default_timezone=tzlocal())

    class Meta:
        model = Like
        fields = (
            'id', 'track', 'track_id', 'user', 'user_id',
            'like', 'updated_at',
        )


class LikeAPISerializer(serializers.Serializer):
    like = serializers.BooleanField(default=False, allow_null=False)

    class Meta:
        model = Like
        fields = (
            'like',
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PlayHistorySerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    track_id = serializers.IntegerField(write_only=True)

    title = serializers.CharField(allow_null=True, allow_blank=True, max_length=200)
    artist = serializers.CharField(allow_null=True, allow_blank=True, max_length=70)

    channel = serializers.ChoiceField(
        choices=CHANNEL, default=DEFAULT_CHANNEL, allow_null=False
    )

    played_at = serializers.DateTimeField(allow_null=False)

    class Meta:
        model = PlayHistory
        fields = (
            'id', 'track', 'track_id', 'artist', 'title', 'channel', 'played_at',
        )


class PlayQueueSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    location = serializers.CharField(allow_null=True, allow_blank=True, max_length=255)
    title = serializers.CharField(allow_null=True, allow_blank=True, max_length=200)
    artist = serializers.CharField(allow_null=True, allow_blank=True, max_length=70)

    class Meta:
        fields = (
            'id', 'location', 'artist', 'title',
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
