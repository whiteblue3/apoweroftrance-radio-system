from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from ..models import (
    JWTBlackList, AccessLog, Profile, User
)

"""
DO NOT import api here!!!
"""


class AccessLogSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        help_text="사용자 이메일", allow_blank=False, required=True, validators=[EmailValidator]
    )
    ip_address = serializers.IPAddressField(help_text="IP 주소", required=True)

    request = serializers.CharField(help_text="요청 API", max_length=255, allow_blank=False, required=True)
    request_body = serializers.CharField(help_text="요청 본문", allow_null=True, allow_blank=True, required=False)
    access_type = serializers.CharField(help_text="타입", max_length=255, allow_blank=False, required=True)
    access_status = serializers.CharField(help_text="처리결과", max_length=255, allow_blank=False, required=True)

    class Meta:
        model = AccessLog
        fields = [
            'email', 'ip_address',
            'request', 'request_body', 'access_type', 'access_status',
        ]


class JWTBlackListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(allow_blank=False, validators=[EmailValidator])
    token = serializers.CharField(max_length=255)
    ip_address = serializers.IPAddressField(allow_blank=False)
    expire_at = serializers.DateTimeField()
    log_ref = AccessLogSerializer(required=False)

    class Meta:
        model = JWTBlackList
        fields = [
            'email', 'ip_address', 'token', 'expire_at', 'log_ref'
        ]


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source='user.email', read_only=True, validators=[EmailValidator]
    )

    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    nickname = serializers.CharField(help_text="닉네임", required=True)

    bio = serializers.CharField(help_text="자기소개", allow_blank=True, required=False)
    image = serializers.CharField(help_text="프로필 이미지", allow_blank=True, required=False, read_only=True)

    homepage = serializers.URLField(
        help_text="홈페이지", allow_blank=True, required=False, validators=[URLValidator(schemes=['http', 'https'])]
    )
    youtube = serializers.URLField(
        help_text="유튜브 채널", allow_blank=True, required=False, validators=[URLValidator(schemes=['http', 'https'])]
    )
    twitter = serializers.URLField(
        help_text="트위터", allow_blank=True, required=False, validators=[URLValidator(schemes=['http', 'https'])]
    )
    facebook = serializers.URLField(
        help_text="페이스북", allow_blank=True, required=False, validators=[URLValidator(schemes=['http', 'https'])]
    )

    class Meta:
        model = Profile
        fields = (
            'email', 'first_name', 'last_name',
            'nickname',
            'bio', 'image',
            'homepage', 'youtube', 'twitter', 'facebook',
        )

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    password_old = serializers.CharField(
        max_length=128,
        min_length=9,
        write_only=True
    )

    password = serializers.CharField(
        max_length=128,
        min_length=9,
        write_only=True
    )

    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('password_old', 'password', 'profile')

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        password_old = validated_data.pop('password_old', None)
        password = validated_data.pop('password', None)

        profile_data = validated_data.pop('profile', {})

        if password is not None and password_old is None:
            raise ValidationError({"password": _("잘못된 파라미터 입력")})

        if password is None and password_old is not None:
            raise ValidationError({"password": _("잘못된 파라미터 입력")})

        if password is not None and password_old is not None:
            if password == password_old:
                raise ValidationError({"password": _("같은 비밀번호로 변경할수 없습니다")})

            try:
                user = authenticate(username=instance.email, password=password_old)
            except User.DoesNotExist:
                user = None

            if user is None:
                raise ValidationError({"password": _("현재 비밀번호가 일치하지 않습니다")})

            instance.set_password(password)

        for (key, value) in validated_data.items():
            if "password" in key:
                instance.login_redirect = "/"
            setattr(instance, key, value)

        instance.save()

        for (key, value) in profile_data.items():
            setattr(instance.profile, key, value)

        instance.profile.save()

        instance.workskill.save()

        return instance
