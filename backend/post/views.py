import json
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import Serializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_utils import api
from django_utils.api import method_permission_classes
from radio.models import Track
from .models import (
    Comment, DirectMessage, Notification, NotificationUser, NOTIFICATION_CATEGORY_LIST
)
from .serializers import (
    CommentSerializer, PostCommentSerializer,
    DirectMessageSerializer, PostDirectMessageSerializer,
    NotificationSerializer
)
from .util import now


class CommentListAPI(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="track_id",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Track ID",
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
            default=100
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

    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        operation_summary="View comment list for track",
        operation_description="Public API",
        manual_parameters=manual_parameters,
        responses={'200': CommentSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        try:
            track_id = request.GET["track_id"]
        except MultiValueDictKeyError:
            raise ValidationError(_("Invalid track_id"))

        try:
            page = int(request.GET["page"])
        except MultiValueDictKeyError:
            page = 0

        try:
            limit = int(request.GET["limit"])
        except MultiValueDictKeyError:
            limit = 100

        try:
            sort = request.GET["sort"]
        except MultiValueDictKeyError:
            sort = "created_at"

        try:
            order = request.GET["order"]
        except MultiValueDictKeyError:
            order = "desc"

        sort_field = sort
        if order == "desc":
            sort_field = "-%s" % sort

        queryset = Comment.objects.filter(Q(track_id=track_id))
        comments = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        search_list = []

        for comment in comments:
            serializer = CommentSerializer(comment)
            search_list.append(serializer.data)

        response = {
            "list": search_list,
            "total": queryset.count()
        }

        return api.response_json(response, status.HTTP_200_OK)


class PostCommentAPI(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = PostCommentSerializer

    @swagger_auto_schema(
        operation_summary="Post comment to track",
        operation_description="Authenticate Required.",
        responses={'200': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        request_data = self.serializer_class(data=request.data)
        request_data.is_valid(raise_exception=True)

        try:
            track = Track.objects.get(id=request.data["track_id"])
        except Track.DoesNotExist:
            raise ValidationError(_("Music does not exist"))

        serializer = CommentSerializer(
            data={
                "user_id": request.user.id,
                "track_id": request.data["track_id"],
                "message": request.data["message"],
                "created_at": now(),
                "updated_at": now(),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


class DirectMessageListAPI(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="send_user_id",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="Send User ID",
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
            default=100
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
    serializer_class = DirectMessageSerializer

    @swagger_auto_schema(
        operation_summary="View direct message list for send user",
        operation_description="Authenticate Required.",
        manual_parameters=manual_parameters,
        responses={'200': DirectMessageSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            send_user_id = request.GET["send_user_id"]
        except MultiValueDictKeyError:
            send_user_id = None

        try:
            page = int(request.GET["page"])
        except MultiValueDictKeyError:
            page = 0

        try:
            limit = int(request.GET["limit"])
        except MultiValueDictKeyError:
            limit = 100

        try:
            sort = request.GET["sort"]
        except MultiValueDictKeyError:
            sort = "created_at"

        try:
            order = request.GET["order"]
        except MultiValueDictKeyError:
            order = "desc"

        sort_field = sort
        if order == "desc":
            sort_field = "-%s" % sort

        if send_user_id is not None:
            queryset = DirectMessage.objects.filter(Q(target_user_id=user.id) & Q(send_user_id=send_user_id))
        else:
            queryset = DirectMessage.objects.filter(Q(target_user_id=user.id))
        messages = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        search_list = []

        for message in messages:
            serializer = DirectMessageSerializer(message)
            search_list.append(serializer.data)

        response = {
            "list": search_list,
            "total": queryset.count()
        }

        return api.response_json(response, status.HTTP_200_OK)


class PostDirectMessageAPI(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = PostDirectMessageSerializer

    @swagger_auto_schema(
        operation_summary="Post direct message to user",
        operation_description="Authenticate Required.",
        responses={'200': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        request_data = self.serializer_class(data=request.data)
        request_data.is_valid(raise_exception=True)

        try:
            User = get_user_model()
            target_user = User.objects.get(id=request.data["target_user_id"])
        except User.DoesNotExist:
            raise ValidationError(_("User does not exist"))

        serializer = DirectMessageSerializer(
            data={
                "send_user_id": request.user.id,
                "target_user_id": request.data["target_user_id"],
                "message": request.data["message"],
                "created_at": now(),
                "updated_at": now(),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


class NotificationListAPI(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="category",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="Category",
            enum=NOTIFICATION_CATEGORY_LIST,
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
            default=10
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
    serializer_class = NotificationSerializer

    @swagger_auto_schema(
        operation_summary="View notification list for track",
        operation_description="Authenticate Required.",
        manual_parameters=manual_parameters,
        responses={'200': NotificationSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            category = request.GET["category"]
        except MultiValueDictKeyError:
            category = None

        if category is not None:
            if category not in NOTIFICATION_CATEGORY_LIST:
                raise ValidationError(_("Invalid category"))

        try:
            page = int(request.GET["page"])
        except MultiValueDictKeyError:
            page = 0

        try:
            limit = int(request.GET["limit"])
        except MultiValueDictKeyError:
            limit = 100

        try:
            sort = request.GET["sort"]
        except MultiValueDictKeyError:
            sort = "created_at"

        try:
            order = request.GET["order"]
        except MultiValueDictKeyError:
            order = "desc"

        sort_field = sort
        if order == "desc":
            sort_field = "-%s" % sort

        targets = NotificationUser.objects.filter(Q(user_id=user.id))

        if category is not None:
            queryset = Notification.objects.filter(
                Q(category=category) & (Q(targets__id__in=targets) | Q(targets__id__isnull=True))
            )
        else:
            queryset = Notification.objects.filter(
                Q(targets__id__in=targets) | Q(targets__id__isnull=True)
            )
        notifications = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        search_list = []

        for notification in notifications:
            serializer = NotificationSerializer(notification)
            search_list.append(serializer.data)

        response = {
            "list": search_list,
            "total": queryset.count()
        }

        return api.response_json(response, status.HTTP_200_OK)
