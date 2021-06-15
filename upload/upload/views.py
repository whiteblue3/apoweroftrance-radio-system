from datetime import timedelta
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView, UpdateAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import Serializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_utils import api, storage
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3
from radio.models import (
    SUPPORT_FORMAT, FORMAT_MP3, FORMAT_M4A, SERVICE_CHANNEL, Track
)
from radio.serializers import TrackSerializer
from .util import now


class UploadAPI(CreateAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="audio",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True,
            description="Music File"
        ),
        openapi.Parameter(
            name="cover_art",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=False,
            description="Cover Art"
        ),
        openapi.Parameter(
            name="format",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="File Format",
            enum=SUPPORT_FORMAT
        ),
        openapi.Parameter(
            name="artist",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="Artist"
        ),
        openapi.Parameter(
            name="title",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="Music Title"
        ),
        openapi.Parameter(
            name="description",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=False,
            description="Music Description"
        ),
        openapi.Parameter(
            name="bpm",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="BPM"
        ),
        openapi.Parameter(
            name="scale",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=False,
            description="Music Scale"
        ),
        openapi.Parameter(
            name="channel",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_ARRAY,
            required=True,
            description="Service Channel",
            items=openapi.Items(type=openapi.TYPE_STRING, enum=SERVICE_CHANNEL)
        ),
        openapi.Parameter(
            name="is_service",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_BOOLEAN,
            required=False,
            default=True,
            description="Service Enable"
        ),
    ]

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = Serializer

    @swagger_auto_schema(
        operation_summary="Upload Music",
        operation_description="Authentication required",
        manual_parameters=manual_parameters,
        operation_id='upload_music',
        responses={'201': TrackSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        user = request.user

        if len(request.FILES.getlist('audio')) > 1:
            raise ValidationError(_("You must select ONE file"))
        elif len(request.FILES.getlist('audio')) < 1:
            raise ValidationError(_("You must select music file"))

        if len(request.FILES.getlist('cover_art')) > 1:
            raise ValidationError(_("You must select ONE file"))

        try:
            audio_format = request.data["format"]
        except MultiValueDictKeyError:
            raise ValidationError(_("Please select file format"))

        if audio_format not in SUPPORT_FORMAT:
            raise ValidationError(_("Unsupported music file format"))

        try:
            artist = request.data["artist"]
        except MultiValueDictKeyError:
            raise ValidationError(_("'artist' is required"))

        if len(artist) > 70:
            raise ValidationError(_("'artist' size is under 70"))

        try:
            title = request.data["title"]
        except MultiValueDictKeyError:
            raise ValidationError(_("'title' is required"))

        if len(title) > 200:
            raise ValidationError(_("'title' size is under 200"))

        try:
            description = request.data["description"]
        except MultiValueDictKeyError:
            description = ""

        try:
            bpm = int(request.data["bpm"])
        except MultiValueDictKeyError:
            bpm = None

        try:
            scale = request.data["scale"]
        except MultiValueDictKeyError:
            scale = None

        if scale is not None and len(scale) > 15:
            raise ValidationError(_("'scale' size is under 15"))

        try:
            channel = request.data["channel"]
        except MultiValueDictKeyError:
            raise ValidationError(_("'channel' is required"))

        channel = channel.replace('"', '').split(',')

        for service_channel in channel:
            if service_channel not in SERVICE_CHANNEL:
                raise ValidationError(_("Invalid service channel"))

        try:
            is_service = request.data["is_service"]
        except MultiValueDictKeyError:
            is_service = True

        duration = None
        filepath = None
        for f in request.FILES.getlist('audio'):
            try:
                storage_driver = settings.STORAGE_DRIVER
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
                    raise ValidationError(_("Unsupported music file format"))
            except Exception as e:
                raise e

            if audio_format == FORMAT_MP3:
                audio = MP3(f, ID3=EasyID3)
                duration = audio.info.length

            elif audio_format == FORMAT_M4A:
                audio = MP4(f)
                duration = audio.info.length

        cover_art_path = None
        for cover_art in request.FILES.getlist('cover_art'):
            try:
                storage_driver = settings.STORAGE_DRIVER
                valid_mimetype = [
                    "image/png"
                ]
                if valid_mimetype is not None:
                    cover_art_path = storage.upload_file_direct(cover_art, 'cover_art', storage_driver, valid_mimetype)
                else:
                    raise ValidationError(_("Unsupported image file format"))
            except Exception as e:
                raise e

        if filepath is not None and duration is not None:
            serializer = TrackSerializer(
                data={
                    "user_id": user.id,
                    "location": filepath,
                    "format": audio_format,
                    "is_service": is_service,
                    "cover_art": cover_art_path,
                    "artist": artist,
                    "title": title,
                    "description": description,
                    "bpm": bpm,
                    "scale": scale,
                    "duration": str(timedelta(seconds=float(duration))),
                    "play_count": 0,
                    "like_count": 0,
                    "channel": channel,
                    "uploaded_at": now(),
                    "last_played_at": None,
                    "is_ban": False,
                    "ban_reason": "",
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            raise ValidationError(_("Music upload failed"))

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


class ReplaceAPI(CreateAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="id",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="Track ID"
        ),
        openapi.Parameter(
            name="audio",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=False,
            description="Music File"
        ),
        openapi.Parameter(
            name="cover_art",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=False,
            description="Cover Art"
        ),
        openapi.Parameter(
            name="format",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="File Format",
            enum=SUPPORT_FORMAT
        ),
    ]

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = Serializer

    @swagger_auto_schema(
        operation_summary="Replace Music or Cover Art",
        operation_description="Authentication required",
        manual_parameters=manual_parameters,
        operation_id='replace_music',
        responses={'201': TrackSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        user = request.user

        try:
            track_id = request.data["id"]
        except MultiValueDictKeyError:
            raise ValidationError(_("id field is required"))

        is_exist_audio = False
        is_exist_image = False

        if len(request.FILES.getlist('audio')) > 1:
            raise ValidationError(_("You must select ONE file"))
        elif len(request.FILES.getlist('audio')) < 1:
            is_exist_audio = False
        else:
            is_exist_audio = True

        if len(request.FILES.getlist('cover_art')) > 1:
            raise ValidationError(_("You must select ONE file"))
        elif len(request.FILES.getlist('cover_art')) < 1:
            is_exist_image = False
        else:
            is_exist_image = True

        if is_exist_audio is False and is_exist_image is False:
            raise ValidationError(_("You must exist audio or image on request"))

        try:
            audio_format = request.data["format"]
        except MultiValueDictKeyError:
            raise ValidationError(_("Please select file format"))

        if audio_format not in SUPPORT_FORMAT:
            raise ValidationError(_("Unsupported music file format"))

        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise ValidationError(_("Music does not exist"))

        if user.id != track.user.id:
            raise ValidationError(_("Invalid access"))

        prev_filepath = track.location
        prev_cover_art_path = track.cover_art

        duration = None
        filepath = None
        for f in request.FILES.getlist('audio'):
            try:
                storage_driver = settings.STORAGE_DRIVER
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
                    raise ValidationError(_("Unsupported music file format"))
            except Exception as e:
                raise e

            if audio_format == FORMAT_MP3:
                audio = MP3(f, ID3=EasyID3)
                duration = audio.info.length

            elif audio_format == FORMAT_M4A:
                audio = MP4(f)
                duration = audio.info.length

            if filepath is not None and duration is not None:
                track.location = filepath
                splitted_prev_location = prev_filepath.split('/')
                prev_filename = splitted_prev_location.pop()
                prev_path = "/".join(splitted_prev_location)
                try:
                    if prev_filepath is not None:
                        if storage.exist_file(prev_path, prev_filename, storage_driver):
                            storage.delete_file(prev_path, prev_filename, storage_driver)
                except Exception as e:
                    # 파일이 존재하지 않는 경우 이곳으로 온다
                    pass

        cover_art_path = None
        for cover_art in request.FILES.getlist('cover_art'):
            try:
                storage_driver = settings.STORAGE_DRIVER
                valid_mimetype = [
                    "image/png"
                ]
                if valid_mimetype is not None:
                    cover_art_path = storage.upload_file_direct(cover_art, 'cover_art', storage_driver, valid_mimetype)
                else:
                    raise ValidationError(_("Unsupported image file format"))
            except Exception as e:
                raise e

            if cover_art_path is not None:
                track.cover_art = cover_art_path
                if prev_cover_art_path is not None:
                    splitted_prev_cover_art_path = prev_cover_art_path.split('/')
                    prev_cover_art_filename = splitted_prev_cover_art_path.pop()
                    prev_cover_art_filepath = "/".join(splitted_prev_cover_art_path)
                    try:
                        if prev_cover_art_path is not None:
                            if storage.exist_file(prev_cover_art_filepath, prev_cover_art_filename, storage_driver):
                                storage.delete_file(prev_cover_art_filepath, prev_cover_art_filename, storage_driver)
                    except Exception as e:
                        # 파일이 존재하지 않는 경우 이곳으로 온다
                        pass

        track.save()

        serializer = TrackSerializer(track)
        return api.response_json(serializer.data, status.HTTP_200_OK)
