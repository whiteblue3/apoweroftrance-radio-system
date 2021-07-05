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
from rest_framework.generics import RetrieveAPIView, CreateAPIView, DestroyAPIView
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
    Claim, ClaimReply, Comment, DirectMessage, Notification, NotificationUser,
    CLAIM_CATEGORY_SPAMUSER, CLAIM_CATEGORY_COPYRIGHT,
    CLAIM_STATUS_OPENED, CLAIM_STATUS_ACCEPT, CLAIM_STATUS_CLOSED,
    CLAIM_STAFF_ACTION_NOACTION, CLAIM_STAFF_ACTION_APPROVED, CLAIM_STAFF_ACTION_LIST,
    CLAIM_CATEGORY_LIST, CLAIM_STATUS_LIST, CLAIM_STAFF_ACTION, NOTIFICATION_CATEGORY_LIST
)
from .serializers import (
    ClaimSerializer, PostClaimSerializer, UpdateClaimSerializer,
    UpdateClaimStatusSerializer, UpdateClaimStaffActionSerializer,
    ClaimReplySerializer, PostClaimReplySerializer,
    CommentSerializer, PostCommentSerializer,
    DirectMessageSerializer, PostDirectMessageSerializer,
    NotificationSerializer
)
from .util import now


class PostClaimAPI(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = PostClaimSerializer

    @swagger_auto_schema(
        operation_summary="Post new claim",
        operation_description="Authenticate Required.",
        responses={'200': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            category = request.data["category"]
        except MultiValueDictKeyError:
            raise ValidationError(_("Category is required"))

        if category not in CLAIM_CATEGORY_LIST:
            raise ValidationError(_("Invalid category"))

        try:
            user_id = request.data["user_id"]
        except KeyError:
            user_id = None

        try:
            track_id = request.data["track_id"]
        except KeyError:
            track_id = None

        if category == CLAIM_CATEGORY_SPAMUSER and user_id is None:
            raise ValidationError(_("Spamuser category required user_id"))

        if category == CLAIM_CATEGORY_COPYRIGHT and track_id is None:
            raise ValidationError(_("Copyright category required track_id"))

        if user_id is not None:
            try:
                User = get_user_model()
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError(_("User does not exist"))

        if track_id is not None:
            try:
                track = Track.objects.get(id=track_id)
            except Track.DoesNotExist:
                raise ValidationError(_("Track does not exist"))

        data = request.data
        data["issuer_id"] = user.id
        data["status"] = CLAIM_STATUS_OPENED
        data["staff_action"] = CLAIM_STAFF_ACTION_NOACTION

        serializer = ClaimSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


class UpdateClaimAPI(api.UpdatePUTAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = UpdateClaimSerializer

    @swagger_auto_schema(
        operation_summary="Update claim",
        operation_description="Authenticate Required.",
        responses={'200': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def put(self, request, *args, **kwargs):
        user = request.user
        try:
            claim_id = request.data["claim_id"]
        except MultiValueDictKeyError:
            raise ValidationError(_("claim_id is required"))

        try:
            category = request.data["category"]
        except MultiValueDictKeyError:
            raise ValidationError(_("Category is required"))

        if category not in CLAIM_CATEGORY_LIST:
            raise ValidationError(_("Invalid category"))

        try:
            user_id = request.data["user_id"]
        except KeyError:
            user_id = None

        try:
            track_id = request.data["track_id"]
        except KeyError:
            track_id = None

        if category == CLAIM_CATEGORY_SPAMUSER and user_id is None:
            raise ValidationError(_("Spamuser category required user_id"))

        if category == CLAIM_CATEGORY_COPYRIGHT and track_id is None:
            raise ValidationError(_("Copyright category required track_id"))

        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            raise ValidationError(_("Claim does not exist"))

        if user_id is not None:
            try:
                User = get_user_model()
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError(_("User does not exist"))

        if track_id is not None:
            try:
                track = Track.objects.get(id=track_id)
            except Track.DoesNotExist:
                raise ValidationError(_("Track does not exist"))

        if user.is_staff is False:
            if claim.issuer.id != user.id:
                raise ValidationError(_('Invalid access'))

        data = request.data
        data["issuer_id"] = claim.issuer_id
        data["status"] = claim.status
        data["staff_action"] = claim.staff_action

        serializer = ClaimSerializer(claim, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


class ClaimListAPI(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="keyword",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="Keyword",
            default=None,
        ),
        openapi.Parameter(
            name="category",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="Category",
            default=None,
            enum=CLAIM_CATEGORY_LIST,
        ),
        openapi.Parameter(
            name="status",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="Status",
            default=None,
            enum=CLAIM_STATUS_LIST,
        ),
        openapi.Parameter(
            name="staff_action",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="Staff Action",
            default=None,
            enum=CLAIM_STAFF_ACTION_LIST,
        ),
        openapi.Parameter(
            name="show_all",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
            required=False,
            description="Show All",
            default=False,
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
    serializer_class = ClaimSerializer

    @swagger_auto_schema(
        operation_summary="View claim list",
        operation_description="Authenticate Required.",
        manual_parameters=manual_parameters,
        responses={'200': ClaimSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            keyword = request.GET["keyword"]
        except MultiValueDictKeyError:
            keyword = None

        try:
            category = request.GET["category"]
        except MultiValueDictKeyError:
            category = None

        try:
            claim_status = request.GET["status"]
        except MultiValueDictKeyError:
            claim_status = None

        try:
            staff_action = request.GET["staff_action"]
        except MultiValueDictKeyError:
            staff_action = None

        try:
            if request.GET["show_all"] == "true":
                show_all = True
            else:
                show_all = False
        except MultiValueDictKeyError:
            show_all = False

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

        sort_field = sort
        if order == "desc":
            sort_field = "-%s" % sort

        filter_category = Q(category=category)
        filter_status = Q(status=claim_status)
        filter_staff_action = Q(staff_action=staff_action)

        filter_staff_permission = Q(accepter_id=user.id) | Q(accepter_id__isnull=True)
        filter_user_permission = Q(issuer_id=user.id)

        if user.is_staff is True:
            if show_all is True:
                queryset = Claim.objects.all()
            else:
                queryset = Claim.objects.filter(filter_staff_permission | filter_user_permission)
        else:
            queryset = Claim.objects.filter(filter_user_permission)

        if category is not None:
            queryset = queryset.filter(filter_category)
        if claim_status is not None:
            queryset = queryset.filter(filter_status)
        if staff_action is not None:
            queryset = queryset.filter(filter_staff_action)

        if keyword is not None:
            filter_claim = Q(issue__icontains=keyword) | Q(reason__icontains=keyword)
            filter_issuer = Q(issuer__profile__nickname__icontains=keyword)
            filter_accepter = Q(accepter__profile__nickname__icontains=keyword)
            filter_targetuser = Q(user__profile__nickname__icontains=keyword)
            filter_targettrack = Q(track__artist__icontains=keyword) | Q(track__title__icontains=keyword) | Q(track__user__profile__nickname__icontains=keyword)

            queryset = queryset.filter(
                filter_claim | filter_issuer | filter_accepter | filter_targetuser | filter_targettrack
            )

        claims = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        search_list = []

        for claim in claims:
            serializer = self.serializer_class(claim)
            search_list.append(serializer.data)

        response = {
            "list": search_list,
            "total": queryset.count()
        }

        return api.response_json(response, status.HTTP_200_OK)


class ClaimRetrieveAPI(RetrieveAPIView):
    schema = openapi.Schema(
        title="Get detail of claim",
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter('claim_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Claim ID")
        ],
    )
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ClaimSerializer

    @swagger_auto_schema(operation_summary=schema.title,
                         manual_parameters=schema.manual_parameters,
                         responses={'200': ClaimSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, claim_id, *args, **kwargs):
        user = request.user
        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            raise ValidationError(_('Claim does not exist'))

        if user.is_staff is False:
            if claim.issuer.id != user.id:
                raise ValidationError(_('Invalid access'))

        serializer = self.serializer_class(claim)

        return api.response_json(serializer.data, status.HTTP_200_OK)


class UpdateClaimStatusAPI(api.UpdatePUTAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = UpdateClaimStatusSerializer

    @swagger_auto_schema(
        operation_summary="Update claim status",
        operation_description="Authenticate Required.",
        responses={'202': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def put(self, request, *args, **kwargs):
        user = request.user

        try:
            claim_id = request.data["claim_id"]
        except KeyError:
            claim_id = None

        if claim_id is None:
            raise ValidationError(_("claim_id is required"))

        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            raise ValidationError(_("Claim does not exist"))

        try:
            claim_status = request.data["status"]
        except MultiValueDictKeyError:
            raise ValidationError(_("status is required"))

        if claim_status not in [CLAIM_STATUS_OPENED, CLAIM_STATUS_CLOSED]:
            raise ValidationError(_("Invalid status"))

        if user.is_staff is False:
            if claim.issuer.id != user.id:
                raise ValidationError(_('Invalid access'))

        data = {
            "status": claim_status
        }

        serializer = ClaimSerializer(claim, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_202_ACCEPTED)


class AcceptClaimAPI(api.UpdatePUTAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = None

    @swagger_auto_schema(
        operation_summary="Accept claim",
        operation_description="Staff Only",
        responses={'202': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def put(self, request, claim_id, *args, **kwargs):
        user = request.user

        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            raise ValidationError(_("Claim does not exist"))

        if user.is_staff is False:
            raise ValidationError(_('Invalid access'))

        data = {
            "accepter_id": user.id
        }

        serializer = ClaimSerializer(claim, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_202_ACCEPTED)


class UpdateClaimStaffActionAPI(api.UpdatePUTAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = UpdateClaimStaffActionSerializer

    @swagger_auto_schema(
        operation_summary="Update claim staff action",
        operation_description="Staff Only",
        responses={'202': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def put(self, request, *args, **kwargs):
        user = request.user

        try:
            claim_id = request.data["claim_id"]
        except KeyError:
            claim_id = None

        if claim_id is None:
            raise ValidationError(_("claim_id is required"))

        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            raise ValidationError(_("Claim does not exist"))

        try:
            staff_action = request.data["staff_action"]
        except MultiValueDictKeyError:
            raise ValidationError(_("staff_action is required"))

        if staff_action not in CLAIM_STAFF_ACTION_LIST:
            raise ValidationError(_("Invalid status"))

        if user.is_staff is False:
            raise ValidationError(_('Invalid access'))

        if claim.staff_action != CLAIM_STAFF_ACTION_APPROVED and staff_action == CLAIM_STAFF_ACTION_APPROVED:
            if claim.category == CLAIM_CATEGORY_SPAMUSER and claim.user_id is not None:
                claim.user.profile.is_ban = True
                if claim.user.profile.ban_reason is None:
                    claim.user.profile.ban_reason = "- [SpamUser] Claim #%s issue: %s" % (claim_id, claim.issue)
                else:
                    claim.user.profile.ban_reason = "- [SpamUser] Claim #%s issue: %s\n%s" % (claim_id, claim.issue, claim.user.profile.ban_reason)
                claim.user.profile.save()
            elif claim.category == CLAIM_CATEGORY_COPYRIGHT and claim.track_id is not None:
                claim.track.is_ban = True
                if claim.track.ban_reason is None:
                    claim.track.ban_reason = "- [Copyright] Claim #%s issue: %s" % (claim_id, claim.issue)
                else:
                    claim.track.ban_reason = "- [Copyright] Claim #%s issue: %s\n%s" % (claim_id, claim.issue, claim.track.ban_reason)
                claim.track.save()
            else:
                raise ValidationError(_('Invalid action'))

        data = {
            "staff_action": staff_action
        }

        serializer = ClaimSerializer(claim, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_202_ACCEPTED)


class ClaimReplyListAPI(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="claim_id",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Claim ID",
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
            default="asc"
        ),
    ]

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ClaimReplySerializer

    @swagger_auto_schema(
        operation_summary="View claim reply list",
        operation_description="Authenticate Required.",
        manual_parameters=manual_parameters,
        responses={'200': ClaimReplySerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            claim_id = int(request.GET["claim_id"])
        except MultiValueDictKeyError:
            raise ValidationError(_("claim_id is required"))

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
            order = "asc"

        sort_field = sort
        if order == "desc":
            sort_field = "-%s" % sort

        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            raise ValidationError(_('Claim does not exist'))

        if user.is_staff is False:
            if claim.issuer.id != user.id:
                raise ValidationError(_('Invalid access'))

        queryset = ClaimReply.objects.filter(Q(claim_id=claim_id))
        replies = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        search_list = []

        for reply in replies:
            serializer = self.serializer_class(reply)
            search_list.append(serializer.data)

        response = {
            "list": search_list,
            "total": queryset.count()
        }

        return api.response_json(response, status.HTTP_200_OK)


class PostClaimReplyAPI(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = PostClaimReplySerializer

    @swagger_auto_schema(
        operation_summary="Post reply to claim",
        operation_description="Authenticate Required.",
        responses={'200': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            claim_id = request.data["claim_id"]
        except MultiValueDictKeyError:
            raise ValidationError(_("claim_id is required"))

        try:
            message = request.data["message"]
        except MultiValueDictKeyError:
            raise ValidationError(_("message is required"))

        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            raise ValidationError(_("Claim does not exist"))

        if user.is_staff is False:
            if claim.issuer.id != user.id:
                raise ValidationError(_('Invalid access'))

        data = request.data
        data["user_id"] = user.id

        serializer = ClaimReplySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


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
            default="asc"
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
            order = "asc"

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
        user = request.user

        if user.profile.is_ban is True:
            raise ValidationError(_("You cannot post comment because you are banned"))

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


class DeleteCommentAPI(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = None

    @swagger_auto_schema(
        operation_summary="Delete comment on track",
        operation_description="Authenticate Required.",
        responses={'200': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def delete(self, request, comment_id, *args, **kwargs):
        user = request.user

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise ValidationError(_("Comment does not exist"))

        if user.id != comment.user.id:
            raise ValidationError(_("Invalid access"))

        comment.delete()

        return api.response_json("OK", status.HTTP_202_ACCEPTED)


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


class DeleteDirectMessageAPI(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = None

    @swagger_auto_schema(
        operation_summary="Delete direct message",
        operation_description="Authenticate Required.",
        responses={'200': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def delete(self, request, message_id, *args, **kwargs):
        user = request.user

        try:
            message = DirectMessage.objects.get(id=message_id)
        except DirectMessage.DoesNotExist:
            raise ValidationError(_("DirectMessage does not exist"))

        if user.id != message.send_user.id:
            raise ValidationError(_("Invalid access"))

        message.delete()

        return api.response_json("OK", status.HTTP_202_ACCEPTED)


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
