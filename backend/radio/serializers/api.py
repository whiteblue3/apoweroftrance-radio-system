from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from ..models import (
    AccessLog, Profile, User
)
from ..error import (
    ProfileDoesNotExist, InvalidAuthentication, UserIsNotActive
)
from .model import (
    ProfileSerializer
)
from . import api


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""
    email = serializers.EmailField(
        help_text="사용자 이메일", allow_blank=False, required=True, validators=[EmailValidator]
    )

    password = serializers.CharField(
        help_text="사용자 패스워드",
        max_length=128,
        min_length=9,
        write_only=True
    )

    password_1 = serializers.CharField(
        help_text="사용자 패스워드 (확인)",
        max_length=128,
        min_length=9,
        write_only=True
    )

    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)

    profile = ProfileSerializer(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_1', 'first_name', 'last_name', 'profile']

    def create(self, validated_data):
        # return User.objects.create_user(**validated_data)

        profile_data = validated_data.pop('profile', {})

        email = validated_data.get('email', None)
        password = validated_data.get('password', None)
        password_1 = validated_data.pop('password_1', None)

        if password != password_1:
            raise ValidationError({"password": _("비밀번호가 일치하지 않습니다")})

        try:
            user_by_email = User.objects.get(
                email=email
            )
        except User.DoesNotExist:
            pass
        else:
            raise ValidationError({"email": _("이미 사용되고 있는 이메일입니다")})

        user = User.objects.create_user(**validated_data)

        try:
            profile = Profile.objects.select_related('user').get(
                user__email=user.email
            )
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        for (key, value) in profile_data.items():
            setattr(profile, key, value)

        user.is_active = False
        user.save()

        profile.save()

        return user


class AuthenticateSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="사용자 이메일", allow_blank=False, required=True,
        validators=[EmailValidator]
    )
    # username = serializers.CharField(help_text="사용자 아이디", max_length=255, required=True)
    password = serializers.CharField(help_text="사용자 패스워드", max_length=128, write_only=True, required=True)
    token = serializers.CharField(help_text="JWT 인증토큰", max_length=255, read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        # username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)

        request = self.context

        # if username is None:
        #     raise InvalidAuthentication

        # Raise an exception if an
        # email is not provided.
        if email is None:
            # raise serializers.ValidationError(
            #     'An email address is required to log in.'
            # )
            raise InvalidAuthentication

        if password is None:
            raise InvalidAuthentication

        user_temp = User.objects.get(email=email)
        if user_temp is not None and user_temp.is_active is False:
            if user_temp.last_login is None:
                raise ValidationError({"is_active": _("활성화 되지 않은 아이디입니다. 이메일 인증을위해 발송된 이메일을 확인해주세요.")})
            else:
                raise ValidationError({"is_active": _("사용이 차단된 사용자입니다")})

        user = authenticate(username=email, password=password, request=request)

        if user is None:
            raise InvalidAuthentication

        if user.is_active is False:
            raise UserIsNotActive

        """Generate JWT Token"""
        ip_address = api.get_client_ip(request)

        (token, expire) = user._generate_jwt_token(remote_ip=ip_address)

        """Notify Security Alert Email"""
        accesslog = AccessLog.objects.filter(email=email).order_by('-accessed_at').distinct()[:30]

        if accesslog.count() > 0:
            for record in accesslog:
                if ip_address != record.ip_address:
                    api.notify_security_email(email, ip_address, token, request, record.id)
                    break

        return {
            'email': user.email,
            'token': token,
        }
