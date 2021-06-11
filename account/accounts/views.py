import jwt
import ast
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import Serializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import JWTBlackList, AccessLog, User, Profile, Follow
from .serializers import (
    AuthenticateSerializer, RegistrationSerializer, UserSerializer, ProfileSerializer,
    JWTBlackListSerializer, FollowSerializer, FollowAPISerializer
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
        operation_summary="Register",
        operation_description="",
        responses={'201': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        util.send_account_activation_email(serializer.data["email"])

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


class DeleteAPI(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Serializer

    @swagger_auto_schema(operation_summary="Delete Account",
                         operation_description="Authentication required",
                         responses={'200': Serializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def delete(self, request, *args, **kwargs):
        request.user.delete()

        return api.response_json("OK", status.HTTP_200_OK)


class AuthenticateAPI(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = AuthenticateSerializer

    @swagger_auto_schema(operation_summary="Signin or Authenticate",
                         responses={'200': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
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


class LogOutAPI(RetrieveAPIView):
    schema = openapi.Schema(
        title="Signout",
        type=openapi.TYPE_OBJECT,
    )

    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = (Serializer,)

    @swagger_auto_schema(operation_summary=schema.title, operation_description="Authentication required")
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        """
        Signout and Invalidate JWT token.
        Invalidate JWT token is process in Authentication Backend automatically.
        """
        ip = api.get_client_ip(request)

        authorization = request.headers.get('Authorization').split(' ')
        token = authorization[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS512'])
        except:
            # msg = 'Invalid authentication. Could not decode token.'
            # raise exceptions.AuthenticationFailed(msg, code=401)
            raise InvalidAuthentication

        orig_iat = payload.get('orig_iat')

        if orig_iat:
            refresh_limit = timedelta(hours=settings.JWT_VALID_HOUR)
            refresh_limit = (refresh_limit.days * 24 * 3600 + refresh_limit.seconds)
            expiration_timestamp = orig_iat + int(refresh_limit)
        else:
            raise InvalidAuthentication

        expire_at = datetime.fromtimestamp(expiration_timestamp).strftime("%Y-%m-%dT%H:%M:%S")

        jwtdata = {
            "email": request.user.email,
            "token": token,
            "ip_address": api.get_client_ip(request),
            "expire_at": expire_at
        }

        old_token = JWTBlackListSerializer(data=jwtdata)
        old_token.is_valid(raise_exception=True)
        old_token.save()

        # Logging Access : Type Logout
        util.accesslog(
            request, ACCESS_TYPE_LOGOUT, ACCESS_STATUS_SUCCESSFUL,
            request.user.email, ip
        )

        return api.response_json("OK", status.HTTP_200_OK)


class ProfileRetrieveAPIView(RetrieveAPIView):
    schema = openapi.Schema(
        title="View specified user's profile",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="User ID")
        ],
    )
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ProfileSerializer

    @swagger_auto_schema(operation_summary=schema.title,
                         manual_parameters=schema.manual_parameters,
                         responses={'200': ProfileSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(_('User does not exist'))

        profile = util.get_profile(user.email)
        serializer = self.serializer_class(profile)

        return api.response_json(serializer.data, status.HTTP_200_OK)


class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(operation_summary="view current signin user\'s profile",
                         operation_description="Authentication required",
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
            description="Profile image"
        )
    ]

    permission_classes = (IsAuthenticated,)
    serializer_class = Serializer
    parser_classes = (MultiPartParser, FormParser,)
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(operation_summary="Modify current signin user\'s profile image",
                         operation_description="Authentication required",
                         manual_parameters=manual_parameters,
                         operation_id='upload_profile_image',
                         responses={'200': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        """Only support JPEG/PNG format image"""
        util.upload_profile_image(request.user.email, request, settings.STORAGE_DRIVER)
        serializer = UserSerializer(request.user)

        return api.response_json(serializer.data, status.HTTP_200_OK)


class UserUpdateAPIView(api.UpdatePUTAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(operation_summary="Modify current signin user's information",
                         operation_description="Authentication required",
                         responses={'200': UserSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def put(self, request, *args, **kwargs):
        """All parameters support partial"""
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_200_OK)


class UserListAPIView(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="keyword",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="Keyword",
            default=None
        ),
        openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Page number",
            default=0
        ),
        openapi.Parameter(
            name="limit",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Limit per page",
            default=30
        ),
        openapi.Parameter(
            name="sort",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description="Sort field",
            default="created_at"
        ),
        openapi.Parameter(
            name="order",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description="Sort order",
            default="desc"
        ),
    ]

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ProfileSerializer

    @swagger_auto_schema(
        operation_summary="View user list",
        operation_description="Authenticate Required.",
        manual_parameters=manual_parameters,
        responses={'200': ProfileSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        try:
            keyword = request.GET["keyword"]
        except MultiValueDictKeyError:
            keyword = None

        try:
            page = int(request.GET["page"])
        except MultiValueDictKeyError:
            page = 0

        try:
            limit = int(request.GET["limit"])
        except MultiValueDictKeyError:
            limit = 30

        try:
            sort = request.GET["sort"]
        except MultiValueDictKeyError:
            sort = "created_at"

        try:
            order = request.GET["order"]
        except MultiValueDictKeyError:
            order = "desc"

        if keyword is None:
            queryset = Profile.objects.filter(user__is_active=True)
        else:
            queryset = Profile.objects.filter(
                Q(user__is_active=True) & Q(nickname__icontains=keyword)
            )

        sort_field = sort
        if order == "desc":
            sort_field = "-%s" % sort

        # tracks = Track.objects.filter(user__id=request.user.id)
        userlist = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        response = []

        for profile in userlist:
            serializer = ProfileSerializer(profile)
            response.append(serializer.data)

        return api.response_json(response, status.HTTP_200_OK)


class FollowerListAPIView(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Page number",
            default=0
        ),
        openapi.Parameter(
            name="limit",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Limit per page",
            default=30
        ),
        openapi.Parameter(
            name="sort",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description="Sort field",
            default="updated_at"
        ),
        openapi.Parameter(
            name="order",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description="Sort order",
            default="desc"
        ),
    ]

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ProfileSerializer

    @swagger_auto_schema(
        operation_summary="List of Followers",
        operation_description="Authentication required",
        manual_parameters=manual_parameters,
        responses={'200': ProfileSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            page = int(request.GET["page"])
        except MultiValueDictKeyError:
            page = 0

        try:
            limit = int(request.GET["limit"])
        except MultiValueDictKeyError:
            limit = 30

        try:
            sort = request.GET["sort"]
        except MultiValueDictKeyError:
            sort = "updated_at"

        try:
            order = request.GET["order"]
        except MultiValueDictKeyError:
            order = "desc"

        queryset = Follow.objects.filter(follow_user_id=user.id, follow=True)

        sort_field = sort
        if order == "desc":
            sort_field = "-%s" % sort

        followers = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        response = []

        for follower in followers:
            try:
                profile = Profile.objects.get(user_id=follower.user.id)
            except Profile.DoesNotExist:
                continue
            serializer = ProfileSerializer(profile)
            response.append(serializer.data)

        return api.response_json(response, status.HTTP_200_OK)


class FollowListAPIView(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Page number",
            default=0
        ),
        openapi.Parameter(
            name="limit",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Limit per page",
            default=30
        ),
        openapi.Parameter(
            name="sort",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description="Sort field",
            default="updated_at"
        ),
        openapi.Parameter(
            name="order",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description="Sort order",
            default="desc"
        ),
    ]

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ProfileSerializer

    @swagger_auto_schema(
        operation_summary="List of Follows",
        operation_description="Authentication required",
        manual_parameters=manual_parameters,
        responses={'200': ProfileSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            page = int(request.GET["page"])
        except MultiValueDictKeyError:
            page = 0

        try:
            limit = int(request.GET["limit"])
        except MultiValueDictKeyError:
            limit = 30

        try:
            sort = request.GET["sort"]
        except MultiValueDictKeyError:
            sort = "updated_at"

        try:
            order = request.GET["order"]
        except MultiValueDictKeyError:
            order = "desc"

        queryset = Follow.objects.filter(user_id=user.id, follow=True)

        sort_field = sort
        if order == "desc":
            sort_field = "-%s" % sort

        follows = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        response = []

        for follow in follows:
            try:
                profile = Profile.objects.get(user_id=follow.follow_user.id)
            except Profile.DoesNotExist:
                continue
            serializer = ProfileSerializer(profile)
            response.append(serializer.data)

        return api.response_json(response, status.HTTP_200_OK)


class FollowAPIView(api.CreateRetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = FollowAPISerializer

    @swagger_auto_schema(
        operation_summary="Get follow status for user",
        operation_description="Authentication required",
        responses={'200': FollowAPISerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, follow_user_id, *args, **kwargs):
        user = request.user
        try:
            follow_user = User.objects.get(id=follow_user_id)
        except User.DoesNotExist:
            raise ValidationError(_("User does not exist"))

        try:
            follow = Follow.objects.get(follow_user_id=follow_user.id, user_id=user.id)
        except Follow.DoesNotExist:
            follow_value = False
        else:
            follow_value = follow.follow

        serializer = FollowAPISerializer(data={
            "follow": follow_value,
        })
        serializer.is_valid(raise_exception=True)

        return api.response_json(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Follow, Unfollow the user",
        operation_description="Authentication required",
        responses={'200': FollowSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, follow_user_id, *args, **kwargs):
        user = request.user
        try:
            follow_value = request.data["follow"]
        except MultiValueDictKeyError:
            follow_value = False

        try:
            follow_user = User.objects.get(id=follow_user_id)
        except User.DoesNotExist:
            raise ValidationError(_("User does not exist"))

        try:
            follow_user_profile = Profile.objects.get(user_id=follow_user_id)
        except Profile.DoesNotExist:
            raise ValidationError(_("Follow user profile does not exist"))

        try:
            user_profile = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            raise ValidationError(_("User profile does not exist"))

        try:
            follow = Follow.objects.get(follow_user_id=follow_user.id, user_id=user.id)
        except Follow.DoesNotExist:
            serializer = FollowSerializer(data={
                "follow_user_id": follow_user.id,
                "user_id": user.id,
                "follow": follow_value,
                "updated_at": str(datetime.now(tz=tzlocal()).isoformat())
            })
            if follow_value is True:
                follow_user_profile.follow_count += 1
                user_profile.following_count += 1
            else:
                follow_user_profile.follow_count -= 1
                user_profile.following_count -= 1
                if follow_user_profile.follow_count < 0:
                    follow_user_profile.follow_count = 0
                if user_profile.following_count < 0:
                    user_profile.following_count = 0
        else:
            serializer = FollowSerializer(follow, data={
                "follow_user_id": follow_user.id,
                "user_id": user.id,
                "follow": follow_value,
                "updated_at": str(datetime.now(tz=tzlocal()).isoformat())
            })
            if follow_value is True:
                if follow.follow is False:
                    follow_user_profile.follow_count += 1
                    user_profile.following_count += 1
            else:
                if follow.follow is True:
                    follow_user_profile.follow_count -= 1
                    user_profile.following_count -= 1
                    if follow_user_profile.follow_count < 0:
                        follow_user_profile.follow_count = 0
                    if user_profile.following_count < 0:
                        user_profile.following_count = 0
        serializer.is_valid(raise_exception=True)
        serializer.save()
        follow_user_profile.save()
        user_profile.save()

        return api.response_json(serializer.data, status.HTTP_200_OK)


class ResetPasswordAPI(RetrieveAPIView):
    schema = openapi.Schema(
        title="Request password reset",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_PATH, type=openapi.TYPE_STRING, description="User email")
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
        Send email that notification of password reset
        Password reset only completed via user click authentication url in email
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(_('%s does not exist user\'s email address' % email))

        profile = util.get_profile(email)
        if profile is not None:
            util.send_reset_password_email(profile.user.email)

        return api.response_json({'payload': 'Sent email'}, status.HTTP_200_OK)


class ConfirmResetPasswordAPI(RetrieveAPIView):
    schema = openapi.Schema(
        title="Confirm password reset",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('auth_code', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="auth code")
        ],
    )
    permission_classes = (AllowAny,)
    serializer_class = Serializer

    @swagger_auto_schema(operation_summary=schema.title,
                         manual_parameters=schema.manual_parameters)
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
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

        profile = util.get_profile(data['email'])
        if profile is not None:
            expire = datetime.strptime(data['expire'], "%Y-%m-%dT%H:%M:%S.%f")
            now = datetime.utcnow()

            if expire.timestamp() < now.timestamp():
                return api.response_json({'error': 'Reset Password Failed for Timeout'})
                # return api.response_url("https://www.gloground.com/resetpasswordfailedfortimeout")

            profile.user.set_password(data['password'])
            profile.user.save()
        else:
            raise UserDoesNotExist

        return api.response_json({'payload': 'OK'})


class ActivateAPI(RetrieveAPIView):
    schema = openapi.Schema(
        title="Activate user account",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('auth_code', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="auth code")
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
        auth_code = request.GET.get('auth_code')

        try:
            decrypted = aes.aes_decrypt(auth_code)
            decrypted_data = decrypted.decode()
            data = ast.literal_eval(decrypted_data[0:-ord(decrypted_data[-1])])
        except Exception as e:
            return api.response_json({'error': 'Account Activation Failed'})
            # return api.response_url("https://www.gloground.com/activate_fail")

        if (
                data['email'] is not None and
                data['date'] is not None and
                data['expire'] is not None
        ) is False:
            return api.response_json({'error': 'Account Activation Failed'})
            # return api.response_url("https://www.gloground.com/activate_fail")

        profile = util.get_profile(data['email'])
        if profile is not None:
            # expire = datetime.strptime(data['expire'], "%Y-%m-%dT%H:%M:%S.%f")
            # now = datetime.utcnow()
            #
            # if expire.timestamp() < now.timestamp():
            #     return api.response_json({'error': 'Account Activation Failed for Timeout'})
            #     # return api.response_url("https://www.gloground.com/activate_fail_timeout")

            profile.user.is_active = True
            if profile.user.is_business is False:
                profile.user.is_uploadable = True
            profile.user.save()
        else:
            raise UserDoesNotExist

        return api.response_json({'payload': 'OK'})
        # return api.response_url("http://%s" % util.get_domain())


class BanJWTAPIView(RetrieveAPIView):
    schema = openapi.Schema(
        title="API to take action when logged in from a different place",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('auth_code', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="auth code")
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
        auth_code = request.GET.get('auth_code')

        try:
            decrypted = aes.aes_decrypt(auth_code)
            decrypted_data = decrypted.decode()
            data = ast.literal_eval(decrypted_data[0:-ord(decrypted_data[-1])])
        except Exception as e:
            return api.response_json({'error': 'Ban JWT Failed. Invalid Auth Code.'})

        if (
                data['email'] is not None and
                data['date'] is not None and
                data['jwt'] is not None and
                data['log'] is not None and
                data['ip_address'] is not None
        ) is False:
            return api.response_json({'error': 'Ban JWT Failed. Invalid Auth Data.'})

        token = data['jwt']
        email = data['email']
        accesslog_pk = data['log']
        ip_address = data['ip_address']

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS512'])
        except:
            # msg = 'Invalid authentication. Could not decode token.'
            # raise exceptions.AuthenticationFailed(msg, code=401)
            return api.response_json({'error': 'Ban JWT Failed. Invalid JWT Token'})

        orig_iat = payload.get('orig_iat')
        refresh_limit = timedelta(hours=settings.JWT_VALID_HOUR)
        refresh_limit = (refresh_limit.days * 24 * 3600 + refresh_limit.seconds)
        expiration_timestamp = orig_iat + int(refresh_limit)

        try:
            accesslog = AccessLog.objects.get(id=accesslog_pk)
        except AccessLog.DoesNotExist:
            return api.response_json({'error': 'Ban JWT Failed. Access Log Not Found'})

        expire_at = datetime.fromtimestamp(expiration_timestamp).strftime("%Y-%m-%dT%H:%M:%S")

        # Logging Access : Type Logout
        util.accesslog(request, ACCESS_TYPE_BAN, ACCESS_STATUS_SUCCESSFUL, email, ip_address)

        try:
            JWTBlackList(
                email=email,
                token=token,
                ip_address=ip_address,
                expire_at=expire_at,
            ).save()
        except:
            return api.response_json({'error': 'Already banned'})

        return api.response_json({'payload': 'OK'})
