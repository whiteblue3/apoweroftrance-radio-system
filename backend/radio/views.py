from datetime import datetime, timedelta
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import Serializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_utils import api, storage
import mutagen.id3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3
from accounts.serializers import UserSerializer
from .models import SUPPORT_FORMAT, FORMAT_MP3, FORMAT_M4A, SERVICE_CHANNEL
from .serializers import TrackSerializer
from .util import now


"""
Namespace: radio

Required API
- [ ] GET list: 모든 서비스중인 트랙. 페이징 처리 필요. AllowAny
- [x] POST upload: 신규 트랙 업로드.
- [ ] GET track/{track_id}: 특정 곡에 대한 정보 조회. AllowAny
- [ ] PUT track/{track_id}: 특정 곡에 대한 정보 수정
- [ ] DELETE track/{track_id}: 트랙 삭제. 플레이큐에서도 제거. 뮤직데몬에도 반영
- [ ] POST like/{track_id}: 사용자가 특정 트랙을 좋아요, 싫어요 및 해제
- [ ] GET playqueue: 현재 플레이 리스트 조회. 페이징 처리 필요. AllowAny

Admin/Staff ONLY
- [ ] POST playqueue/reset: 현재 플레이 리스트를 리셋. 관리자 기능
- [ ] POST queuein/{track_id}: 플레이리스트에 곡추가. 관리자 기능
- [ ] DELETE unqueue/{index}: 지정된 현재 플레이리스트의 인덱스의 곡을 플레이리스트에서 제거, 관리자 기능

Required Callback
- [ ] GET on_startup/{channel}: 서비스 구동시 최초의 플레이 리스트 셋업
- [ ] POST on_play/{channel}: 플레이 History 기록 
- [ ] POST on_stop/{channel}: 새로운 곡을 플레이 리스트에 queuein
"""


class UploadAPI(CreateAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="audio",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True,
            description="음원파일"
        ),
        openapi.Parameter(
            name="format",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="음원포멧",
            enum=SUPPORT_FORMAT
        ),
        openapi.Parameter(
            name="artist",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="아티스트"
        ),
        openapi.Parameter(
            name="title",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="곡 제목"
        ),
        openapi.Parameter(
            name="description",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=False,
            description="곡 설명"
        ),
        openapi.Parameter(
            name="channel",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="서비스 채널",
            enum=SERVICE_CHANNEL
        ),
    ]

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = Serializer

    @swagger_auto_schema(
        operation_summary="음악 업로드",
        operation_description="",
        manual_parameters=manual_parameters,
        operation_id='upload_music',
        responses={'201': TrackSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        user = request.user

        if len(request.FILES.getlist('audio')) > 1:
            raise ValidationError(_("음원파일은 한개만 선택해 주세요"))

        audio_format = request.data["format"]
        if audio_format not in SUPPORT_FORMAT:
            raise ValidationError(_("지원하지 않는 음원포멧"))

        artist = request.data["artist"]
        title = request.data["title"]

        try:
            description = request.data["description"]
        except MultiValueDictKeyError:
            description = ""

        channel = request.data["channel"]

        duration = None
        filepath = None
        for f in request.FILES.getlist('audio'):
            try:
                storage_driver = 'gcs'
                valid_mimetype = None
                if audio_format == FORMAT_MP3:
                    valid_mimetype = [
                        "audio/mpeg", "audio/mp3"
                    ]
                elif audio_format == FORMAT_M4A:
                    valid_mimetype = [
                        "audio/aac", "audio/x-m4a", "audio/mp4", "audio/m4a"
                    ]
                if valid_mimetype is not None:
                    filepath = storage.upload_file_direct(f, 'music', storage_driver, valid_mimetype)
                else:
                    raise ValidationError(_("지원하지 않는 음원포멧"))
            except Exception as e:
                raise e

            if audio_format == FORMAT_MP3:
                audio = MP3(f, ID3=EasyID3)
                duration = audio.info.length

            elif audio_format == FORMAT_M4A:
                audio = MP4(f)
                duration = audio.info.length

        if filepath is not None and duration is not None:
            serializer = TrackSerializer(
                data={
                    "user_id": user.id,
                    "location": filepath,
                    "format": audio_format,
                    "is_service": True,
                    "artist": artist,
                    "title": title,
                    "description": description,
                    "duration": str(timedelta(seconds=float(duration))),
                    "play_count": 0,
                    "channel": [channel],
                    "uploaded_at": now(),
                    "last_played_at": None
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            raise ValidationError(_("업로드 실패"))

        return api.response_json(serializer.data, status.HTTP_201_CREATED)
