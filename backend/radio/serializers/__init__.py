from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from ..models import (
    JWTBlackList, AccessLog, Profile, User
)
from ..error import (
    ProfileDoesNotExist, InvalidAuthentication, UserIsNotActive
)


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.

    example)
    image = Base64ImageField(help_text="프로필 이미지", required=False, max_length=None, use_url=True)
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


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

        return instance


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
        from .. import api

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
