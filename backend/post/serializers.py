from datetime import datetime
from dateutil.tz import tzlocal
from rest_framework import serializers
from accounts.serializers import UserSerializer
from radio.serializers import TrackSerializer
from .models import (
    CLAIM_CATEGORY, CLAIM_STATUS, NOTIFICATION_CATEGORY, Claim, ClaimReply, Comment, Notification
)


class ClaimSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    issuer = UserSerializer(read_only=True)
    issuer_id = serializers.IntegerField(write_only=True, allow_null=False)

    accepter = UserSerializer(read_only=True)
    accepter_id = serializers.IntegerField(write_only=True, allow_null=True)

    category = serializers.ChoiceField(choices=CLAIM_CATEGORY, allow_null=False, allow_blank=False)

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, allow_null=True)

    track = TrackSerializer(read_only=True)
    track_id = serializers.IntegerField(write_only=True, allow_null=True)

    issue = serializers.CharField(allow_null=False, allow_blank=False, max_length=150)
    reason = serializers.CharField(allow_null=False, allow_blank=False, max_length=3000)

    status = serializers.ChoiceField(choices=CLAIM_STATUS, allow_null=False, allow_blank=False)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Claim
        fields = (
            'id',
            'issuer', 'issuer_id', 'accepter', 'accepter_id',
            'category', 'user', 'user_id', 'track', 'track_id',
            'issue', 'reason', 'status',
            'created_at', 'updated_at',
        )


class ClaimReplySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    claim = ClaimSerializer(read_only=True)
    claim_id = serializers.IntegerField(write_only=True, allow_null=False)

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, allow_null=False)

    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=3000)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ClaimReply
        fields = (
            'id',
            'claim', 'claim_id', 'user', 'user_id', 'message',
            'created_at', 'updated_at',
        )


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, allow_null=False)

    track = TrackSerializer(read_only=True)
    track_id = serializers.IntegerField(write_only=True, allow_null=False)

    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=1000)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'user', 'user_id', 'track', 'track_id', 'message',
            'created_at', 'updated_at',
        )


class PostCommentSerializer(serializers.Serializer):
    track_id = serializers.IntegerField(allow_null=False, required=True)
    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=1000, required=True)

    class Meta:
        model = Comment
        fields = (
            'track_id', 'message',
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    category = serializers.ChoiceField(choices=NOTIFICATION_CATEGORY, allow_null=False, allow_blank=False)
    # targets = UserSerializer(many=True)

    title = serializers.CharField(allow_null=False, allow_blank=False, max_length=150)
    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=3000)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id',
            'category',
            'title', 'message',
            'created_at', 'updated_at',
        )
