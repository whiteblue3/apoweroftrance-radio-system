import jwt
import ast
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import Serializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import JWTBlackList, AccessLog, User
from .serializers import (
    AuthenticateSerializer, RegistrationSerializer, UserSerializer, ProfileSerializer,
    JWTBlackListSerializer,
)
from .error import (
    InvalidAuthentication, UserDoesNotExist, UserIsNotActive
)
from .access_log import *
from django_utils import api, aes
from . import util


class RegistrationAPI(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="",
        responses={'201': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


class AuthenticateAPI(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = AuthenticateSerializer

    @swagger_auto_schema(operation_summary="로그인 및 인증",
                         responses={'200': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        """
        로그인 및 사용자 인증을 합니다.
        """
        ip = api.get_client_ip(request)

        try:
            serializer = self.serializer_class(data=request.data, context=request)
            serializer.is_valid(raise_exception=True)
        except InvalidAuthentication:
            util.accesslog(
                request, ACCESS_TYPE_AUTHENTICATE, ACCESS_STATUS_FAIL,
                request.data['email'], ip
            )
            raise InvalidAuthentication
        except UserDoesNotExist:
            util.accesslog(
                request, ACCESS_TYPE_AUTHENTICATE, ACCESS_STATUS_FAIL_USER_NOT_EXIST,
                request.data['email'], ip
            )
            raise UserDoesNotExist
        except UserIsNotActive:
            util.accesslog(
                request, ACCESS_TYPE_AUTHENTICATE, ACCESS_STATUS_FAIL_USER_INACTIVE,
                request.data['email'], ip
            )
            raise UserIsNotActive
        else:
            util.accesslog(
                request, ACCESS_TYPE_AUTHENTICATE, ACCESS_STATUS_SUCCESSFUL,
                request.data['email'], ip
            )

        response = serializer.data
        return api.response_json(response, status.HTTP_200_OK)


class LogOutAPI(APIView):
    schema = openapi.Schema(
        title="로그아웃",
        type=openapi.TYPE_OBJECT,
    )

    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = (Serializer,)

    http_method_names = ["post"]

    @swagger_auto_schema(operation_summary=schema.title)
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        """
        로그아웃 및 JWT 토큰의 무효화.
        JWT 토큰의 무효화는 Authentication Backend에서 자동으로 이루어짐
        """
        ip = api.get_client_ip(request)

        authorization = request.headers.get('Authorization').split(' ')
        token = authorization[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS512')
        except:
            # msg = 'Invalid authentication. Could not decode token.'
            # raise exceptions.AuthenticationFailed(msg, code=401)
            raise InvalidAuthentication

        orig_iat = payload.get('orig_iat')

        if orig_iat:
            refresh_limit = timedelta(hours=36)
            refresh_limit = (refresh_limit.days * 24 * 3600 + refresh_limit.seconds)
            expiration_timestamp = orig_iat + int(refresh_limit)
        else:
            raise InvalidAuthentication

        old_token = JWTBlackListSerializer(data={
            "email": request.user.email,
            "token": token,
            "ip_address": api.get_client_ip(request),
            "expire_at": datetime.fromtimestamp(expiration_timestamp)
        })
        old_token.is_valid(raise_exception=True)
        old_token.save()

        # Logging Access : Type Logout
        util.accesslog(
            request, ACCESS_TYPE_LOGOUT, ACCESS_STATUS_SUCCESSFUL,
            request.user.username, ip
        )

        return api.response_json("OK", status.HTTP_200_OK)


class ProfileRetrieveAPIView(RetrieveAPIView):
    schema = openapi.Schema(
        title="회원 프로필 조회",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_PATH, type=openapi.TYPE_STRING, description="사용자 이메일")
        ],
    )
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ProfileSerializer

    @swagger_auto_schema(operation_summary=schema.title,
                         manual_parameters=schema.manual_parameters,
                         responses={'200': ProfileSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, email, *args, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(_('%s는 존재하지 않는 사용자의 이메일 주소입니다' % email))

        profile = util.get_profile(email)
        serializer = self.serializer_class(profile)

        return api.response_json(serializer.data, status.HTTP_200_OK)


class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(operation_summary="현재 로그인된 사용자 정보 조회",
                         responses={'200': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return api.response_json(serializer.data, status.HTTP_200_OK)


class UserProfileImageUpdateAPIView(CreateAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="image",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True,
            description="프로필 이미지"
        )
    ]

    permission_classes = (IsAuthenticated,)
    serializer_class = Serializer
    parser_classes = (MultiPartParser, FormParser,)
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(operation_summary="현재 로그인된 사용자 프로필 이미지 수정",
                         manual_parameters=manual_parameters,
                         operation_id='upload_profile_image',
                         responses={'200': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        """이미지는 JPEG/PNG 형식만 지원합니다"""
        util.upload_profile_image(request.user.email, request)
        serializer = UserSerializer(request.user)

        return api.response_json(serializer.data, status.HTTP_200_OK)


class UserUpdateAPIView(api.UpdatePUTAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(operation_summary="현재 로그인된 사용자 정보 수정",
                         responses={'200': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def put(self, request, *args, **kwargs):
        """모든 파라미터는 일부분만 업데이트를 지원합니다"""
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_200_OK)


class ResetPasswordAPI(RetrieveAPIView):
    schema = openapi.Schema(
        title="비밀번호 리셋 요청",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_PATH, type=openapi.TYPE_STRING, description="사용자 이메일")
        ],
    )
    permission_classes = (AllowAny,)
    serializer_class = Serializer

    @swagger_auto_schema(operation_summary=schema.title,
                         manual_parameters=schema.manual_parameters)
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, email, *args, **kwargs):
        """
        이메일로 비밀번호 재설정 알림 이메일을 보냅니다
        이메일 안의 링크를 클릭했을때 비로소 비밀번호 재설정이 완료됩니다
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(_('%s는 존재하지 않는 사용자의 이메일 주소입니다' % email))

        profile = api.get_profile(email)
        if profile is not None:
            api.send_reset_password_email(profile.user.email)

        return api.response_json({'payload': 'Sent email'}, status.HTTP_200_OK)


class ConfirmResetPasswordAPI(RetrieveAPIView):
    schema = openapi.Schema(
        title="비밀번호 리셋 확인",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('auth_code', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="인증코드")
        ],
    )
    permission_classes = (AllowAny,)
    serializer_class = Serializer

    @swagger_auto_schema(operation_summary=schema.title,
                         manual_parameters=schema.manual_parameters)
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        """비밀번호 재설정 실패시와 성공시 Redirect 할 페이지가 필요합니다"""
        auth_code = request.GET.get('auth_code')

        try:
            decrypted = aes.aes_decrypt(auth_code)
            decrypted_data = decrypted.decode()
            data = ast.literal_eval(decrypted_data[0:-ord(decrypted_data[-1])])
        except Exception as e:
            return api.response_json({'error': 'Reset Password Failed'})
            # return api.response_url("https://www.gloground.com/resetpasswordfailed")

        if (
            data['email'] is not None and
            data['date'] is not None and
            data['password'] is not None and
            data['expire'] is not None
        ) is False:
            return api.response_json({'error': 'Reset Password Failed'})
            # return api.response_url("https://www.gloground.com/resetpasswordfailed")

        profile = api.get_profile(data['email'])
        if profile is not None:
            expire = datetime.strptime(data['expire'], "%Y-%m-%dT%H:%M:%S.%f")
            now = datetime.utcnow()

            if expire.timestamp() < now.timestamp():
                return api.response_json({'error': 'Reset Password Failed for Timeout'})
                # return api.response_url("https://www.gloground.com/resetpasswordfailedfortimeout")

            # TODO: 패스워드 변경 페이지로 리다이렉트
            profile.user.login_redirect = "/password"
            profile.user.set_password(data['password'])
            profile.user.save()

            """임시 비밀번호 발급 내역은 History에 포함하지 않습니다"""
            # PasswordHistory(email=data['email'], password=data['password'], auth_code=auth_code).save()
        else:
            raise UserDoesNotExist

        return api.response_json({'payload': 'OK'})


class BanJWTAPIView(RetrieveAPIView):
    schema = openapi.Schema(
        title="평소와 다른곳에서 로그인 되었을때 조치를 취하는 API",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('auth_code', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="인증코드")
        ],
    )
    permission_classes = (AllowAny,)
    serializer_class = Serializer

    http_method_names = ['get']

    @swagger_auto_schema(operation_summary=schema.title,
                         manual_parameters=schema.manual_parameters)
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        """실패시와 성공시 Redirect 할 페이지가 필요합니다"""
        auth_code = request.GET.get('auth_code')

        try:
            decrypted = aes.aes_decrypt(auth_code)
            decrypted_data = decrypted.decode()
            data = ast.literal_eval(decrypted_data[0:-ord(decrypted_data[-1])])
        except Exception as e:
            return api.response_json({'error': 'Ban JWT Failed'})

        if (
            data['email'] is not None and
            data['date'] is not None and
            data['jwt'] is not None and
            data['log'] is not None and
            data['ip_address'] is not None
        ) is False:
            return api.response_json({'error': 'Ban JWT Failed'})

        token = data['jwt']
        email = data['email']
        accesslog_pk = data['log']
        ip_address = data['ip_address']

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS512')
        except:
            # msg = 'Invalid authentication. Could not decode token.'
            # raise exceptions.AuthenticationFailed(msg, code=401)
            return api.response_json({'error': 'Ban JWT Failed'})

        orig_iat = payload.get('orig_iat')
        refresh_limit = timedelta(hours=36)
        refresh_limit = (refresh_limit.days * 24 * 3600 + refresh_limit.seconds)
        expiration_timestamp = orig_iat + int(refresh_limit)

        try:
            accesslog = AccessLog.objects.get(id=accesslog_pk)
        except AccessLog.DoesNotExist:
            return api.response_json({'error': 'Ban JWT Failed'})

        JWTBlackList(
            email=email,
            token=token,
            ip_address=ip_address,
            expire_at=datetime.fromtimestamp(expiration_timestamp),
            log_ref=accesslog
        ).save()

        return api.response_json({'payload': 'OK'})
