import json
from datetime import datetime
from dateutil.tz import tzlocal
from rest_framework import serializers
from accounts.serializers import UserSerializer
from radio.serializers import TrackSerializer
from .models import (
    CLAIM_CATEGORY, CLAIM_STATUS, CLAIM_STAFF_ACTION, NOTIFICATION_CATEGORY,
    CLAIM_STATUS_OPENED, CLAIM_STATUS_CLOSED, CLAIM_STAFF_ACTION_NOACTION,
    Claim, ClaimReply, Comment, DirectMessage, Notification
)


class JSONSerializerField(serializers.Field):
    """Serializer for JSONField -- required to make field writable"""

    def to_representation(self, value):
        json_data = {}
        try:
            json_data = json.loads(value)
        except ValueError as e:
            raise e
        finally:
            return json_data

    def to_internal_value(self, data):
        return json.dumps(data)


class ClaimSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    issuer = UserSerializer(read_only=True)
    issuer_id = serializers.IntegerField(write_only=True, allow_null=False)

    accepter = UserSerializer(read_only=True)
    accepter_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    category = serializers.ChoiceField(choices=CLAIM_CATEGORY, allow_null=False, allow_blank=False)

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    track = TrackSerializer(read_only=True)
    track_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    issue = serializers.CharField(allow_null=False, allow_blank=False, max_length=150)
    reason = serializers.CharField(allow_null=False, allow_blank=False, max_length=3000)

    status = serializers.ChoiceField(choices=CLAIM_STATUS, allow_null=False, allow_blank=False)
    staff_action = serializers.ChoiceField(choices=CLAIM_STAFF_ACTION, allow_null=False, allow_blank=False)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Claim
        fields = (
            'id',
            'issuer', 'issuer_id', 'accepter', 'accepter_id',
            'category', 'user', 'user_id', 'track', 'track_id',
            'issue', 'reason', 'status', 'staff_action',
            'created_at', 'updated_at',
        )


class PostClaimSerializer(serializers.ModelSerializer):
    category = serializers.ChoiceField(choices=CLAIM_CATEGORY, required=True, allow_null=False, allow_blank=False)

    user_id = serializers.IntegerField(required=False, allow_null=True)
    track_id = serializers.IntegerField(required=False, allow_null=True)

    issue = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=150)
    reason = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=3000)

    class Meta:
        model = Claim
        fields = (
            'category', 'user_id', 'track_id',
            'issue', 'reason',
        )


class UpdateClaimSerializer(serializers.ModelSerializer):
    claim_id = serializers.IntegerField(write_only=True, allow_null=False)

    category = serializers.ChoiceField(choices=CLAIM_CATEGORY, required=True, allow_null=False, allow_blank=False)

    user_id = serializers.IntegerField(required=False, allow_null=True)
    track_id = serializers.IntegerField(required=False, allow_null=True)

    issue = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=150)
    reason = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=3000)

    class Meta:
        model = Claim
        fields = (
            'claim_id', 'category', 'user_id', 'track_id',
            'issue', 'reason',
        )


class UpdateClaimStatusSerializer(serializers.Serializer):
    claim_id = serializers.IntegerField(write_only=True, allow_null=False)

    status = serializers.ChoiceField(choices=[CLAIM_STATUS_OPENED, CLAIM_STATUS_CLOSED], allow_null=False, allow_blank=False)

    class Meta:
        model = Claim
        fields = (
            'claim_id', 'status',
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UpdateClaimStaffActionSerializer(serializers.Serializer):
    claim_id = serializers.IntegerField(write_only=True, allow_null=False)

    staff_action = serializers.ChoiceField(choices=CLAIM_STAFF_ACTION, allow_null=False, allow_blank=False)

    class Meta:
        model = Claim
        fields = (
            'claim_id', 'staff_action',
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


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


class PostClaimReplySerializer(serializers.ModelSerializer):
    claim_id = serializers.IntegerField(write_only=True, allow_null=False)

    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=3000)

    class Meta:
        model = ClaimReply
        fields = (
            'claim_id', 'message',
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


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


class DirectMessageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    send_user = UserSerializer(read_only=True)
    send_user_id = serializers.IntegerField(write_only=True, allow_null=False)

    target_user = UserSerializer(read_only=True)
    target_user_id = serializers.IntegerField(write_only=True, allow_null=False)

    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=1000)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DirectMessage
        fields = (
            'id',
            'send_user', 'send_user_id', 'target_user', 'target_user_id', 'message',
            'created_at', 'updated_at',
        )


class PostDirectMessageSerializer(serializers.Serializer):
    target_user_id = serializers.IntegerField(allow_null=False, required=True)
    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=1000, required=True)

    class Meta:
        model = DirectMessage
        fields = (
            'target_user_id', 'message',
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
    data = JSONSerializerField(allow_null=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id',
            'category',
            'title', 'message', 'data',
            'created_at', 'updated_at',
        )


class PostNotificationSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=NOTIFICATION_CATEGORY, allow_null=False, allow_blank=False)

    targets = serializers.ListField(
        child=serializers.IntegerField(allow_null=True),
        allow_null=True
    )

    title = serializers.CharField(allow_null=False, allow_blank=False, max_length=150)
    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=3000)
    data = JSONSerializerField(allow_null=True)

    class Meta:
        model = Notification
        fields = (
            'category', 'targets',
            'title', 'message', 'data'
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PostTrackTagSerializer(serializers.Serializer):
    track_id = serializers.IntegerField(write_only=True, required=True, allow_null=False)

    tag = serializers.ListField(
        child=serializers.CharField(allow_null=False, allow_blank=False, max_length=150),
        allow_null=False
    )

    class Meta:
        model = Notification
        fields = (
            'track_id', 'tag',
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
