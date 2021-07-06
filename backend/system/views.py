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
from .models import (
    Config
)
from .serializers import (
    ConfigSerializer
)
from .util import now


class ConfigListAPI(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="key",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="Key",
            default=None,
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

    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ConfigSerializer

    @swagger_auto_schema(
        operation_summary="Get config list",
        operation_description="Public API",
        manual_parameters=manual_parameters,
        responses={'200': ConfigSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        try:
            key = request.GET["key"]
        except MultiValueDictKeyError:
            key = None

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

        queryset = Config.objects.all()

        if key is not None:
            queryset = queryset.filter(Q(key__icontains=key))

        configs = queryset.order_by(sort_field).distinct()[(page * limit):((page * limit) + limit)]
        search_list = []

        for config in configs:
            serializer = self.serializer_class(config)
            search_list.append(serializer.data)

        response = {
            "list": search_list,
            "total": queryset.count()
        }

        return api.response_json(response, status.HTTP_200_OK)
