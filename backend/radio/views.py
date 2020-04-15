from datetime import datetime, timedelta
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
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import Serializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_utils import api, storage
from django_utils.api import method_permission_classes
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3
from .models import (
    SUPPORT_FORMAT, FORMAT_MP3, FORMAT_M4A, SERVICE_CHANNEL,
    Track, Like, PlayQueue
)
from .serializers import (
    TrackSerializer, TrackAPISerializer, LikeSerializer, LikeAPISerializer,
    PlayQueueSerializer, PlayHistorySerializer
)
from .util import now, get_random_track


class TrackListAPI(RetrieveAPIView):
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
    ]
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Serializer

    @swagger_auto_schema(
        operation_summary="Music List",
        operation_description="Public API",
        manual_parameters=manual_parameters,
        responses={'200': TrackSerializer})
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

        if keyword is None:
            queryset = Track.objects.filter(Q(is_service=True))
        else:
            queryset = Track.objects.filter(
                Q(is_service=True) | Q(title__icontains=keyword) | Q(artist__icontains=keyword)
            )

        track_list = queryset.order_by('-uploaded_at').distinct()[(page * limit):((page * limit) + limit)]
        response = []

        for track in track_list:
            serializer = TrackSerializer(track)
            response.append(serializer.data)

        return api.response_json(response, status.HTTP_200_OK)


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
            name="channel",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True,
            description="Service Channel",
            enum=SERVICE_CHANNEL
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
        # TODO: 파일 업로드시 nginx timeout 문제 있음. 업로드는 정상적

        user = request.user

        if len(request.FILES.getlist('audio')) > 1:
            raise ValidationError(_("You must select ONE file"))
        elif len(request.FILES.getlist('audio')) < 1:
            raise ValidationError(_("You must select music file"))

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

        try:
            title = request.data["title"]
        except MultiValueDictKeyError:
            raise ValidationError(_("'title' is required"))

        try:
            description = request.data["description"]
        except MultiValueDictKeyError:
            description = ""

        try:
            channel = request.data["channel"]
        except MultiValueDictKeyError:
            raise ValidationError(_("'channel' is required"))

        if channel not in SERVICE_CHANNEL:
            raise ValidationError(_("Invalid service channel"))

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
            raise ValidationError(_("Music upload failed"))

        return api.response_json(serializer.data, status.HTTP_201_CREATED)


class TrackAPI(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = TrackAPISerializer

    @swagger_auto_schema(
        operation_summary="View music information",
        operation_description="Public API",
        responses={'200': TrackSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    @method_permission_classes((AllowAny,))
    def get(self, request, track_id, *args, **kwargs):
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise ValidationError(_("Music does not exist"))

        serializer = TrackSerializer(track)

        return api.response_json(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Modify music information",
        operation_description="Authentication required. Modify my own music information",
        responses={'202': TrackSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    @method_permission_classes((IsAuthenticated,))
    def put(self, request, track_id, *args, **kwargs):
        user = request.user

        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise ValidationError(_("Music does not exist"))

        if track.user.id == user.id:
            serializer = TrackSerializer(track, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            raise ValidationError(_("You have NOT permission to modify track information"))

        return api.response_json(serializer.data, status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        operation_summary="Delete music",
        operation_description="Authentication required. Delete my own music",
        responses={'202': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    @method_permission_classes((IsAuthenticated,))
    def delete(self, request, track_id, *args, **kwargs):
        user = request.user

        try:
            track = Track.objects.get(id=track_id)
            location = track.location
        except Track.DoesNotExist:
            raise ValidationError(_("Music does not exist"))

        unqueue_list = []
        if track.user.id == user.id:
            # Find index of channel queue
            queuelist = PlayQueue.objects.filter(track_id=track_id)
            if queuelist.count() > 0:
                for queue in queuelist:
                    channel = queue.channel

                    queue_channel = PlayQueue.objects.filter(channel__icontains=channel)
                    index_channel = queue_channel.index(queue)
                    unqueue_list.append((channel, index_channel,))

            location_split = location.split("/")

            storage_driver = 'gcs'
            storage.delete_file('music', location_split[-1], storage_driver)

            track.delete()

            for unqueue_channel, index in unqueue_list:
                api.request_async_threaded("POST", settings.MUSICDAEMON_URL, callback=None, data={
                    "host": "server",
                    "target": unqueue_channel,
                    "command": "unqueue",
                    "data": {
                        "index_at": index
                    }
                })
        else:
            raise ValidationError(_("You have NOT permission to delete track"))

        return api.response_json("OK", status.HTTP_202_ACCEPTED)


class LikeAPI(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = LikeAPISerializer

    @swagger_auto_schema(
        operation_summary="Like, Unlike or not both the music",
        operation_description="Authentication required",
        responses={'200': LikeSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, track_id, *args, **kwargs):
        user = request.user
        try:
            like_value = request.data["like"]
        except MultiValueDictKeyError:
            like_value = None

        try:
            _ = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise ValidationError(_("Music does not exist"))

        try:
            like = Like.objects.get(track_id=track_id, user_id=user.id)
        except Like.DoesNotExist:
            serializer = LikeSerializer(data={
                "track_id": track_id,
                "user_id": user.id,
                "like": like_value,
                "updated_at": now()
            })
        else:
            serializer = LikeSerializer(like, data={
                "track_id": track_id,
                "user_id": user.id,
                "like": like_value,
                "updated_at": now()
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api.response_json(serializer.data, status.HTTP_200_OK)


class PlayQueueAPI(RetrieveAPIView):
    manual_parameters = [
        openapi.Parameter(
            name="channel",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description="Service Channel",
            enum=SERVICE_CHANNEL
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
    ]
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Serializer

    @swagger_auto_schema(
        operation_summary="Play List",
        operation_description="Public API",
        manual_parameters=manual_parameters,
        responses={'200': PlayQueueSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        try:
            channel = request.GET["channel"]
        except MultiValueDictKeyError:
            raise ValidationError(_("'channel' is required parameter"))

        if channel not in SERVICE_CHANNEL:
            raise ValidationError(_("Invalid service channel"))

        try:
            page = int(request.GET["page"])
        except MultiValueDictKeyError:
            page = 0

        try:
            limit = int(request.GET["limit"])
        except MultiValueDictKeyError:
            limit = 30

        queryset = PlayQueue.objects.filter(channel__icontains=channel)

        queue_list = queryset.order_by('id').distinct()[(page * limit):((page * limit) + limit)]
        response = []

        for queue in queue_list:
            serializer = PlayQueueSerializer(queue)
            response.append(serializer.data)

        return api.response_json(response, status.HTTP_200_OK)


class NowPlayingAPI(RetrieveAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(
        operation_summary="Now Playing",
        operation_description="Public API",
        responses={'200': PlayQueueSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, channel, *args, **kwargs):
        queue_list = PlayQueue.objects.filter(channel__icontains=channel).order_by('id').distinct()
        if queue_list.count() > 0:
            queue = queue_list[0]
            track = queue.track

            return api.response_json({
                "id": track.id,
                "location": track.location,
                "artist": track.artist,
                "title": track.title
            }, status.HTTP_200_OK)
        else:
            return api.response_json(None, status.HTTP_200_OK)


class PlayQueueResetAPI(RetrieveAPIView):
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(
        operation_summary="Reset PlayQueue",
        operation_description="Admin Only API",
        responses={'202': PlayQueueSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, channel, *args, **kwargs):
        if channel not in SERVICE_CHANNEL:
            raise ValidationError(_("Invalid service channel"))

        PlayQueue.objects.filter(channel__icontains=channel).delete()

        random_tracks = get_random_track(channel, 30)

        response = []
        response_daemon_data = []
        for track in random_tracks:
            location = track.location
            artist = track.artist
            title = track.title
            serializer = PlayQueueSerializer(data={
                "track_id": track.id,
                "location": location,
                "artist": artist,
                "title": title
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response.append(serializer.data)
            response_daemon_data.append({
                "id": track.id,
                "location": "/srv/media/%s" % location,
                "artist": artist,
                "title": title
            })

        response_daemon = {
            "host": "server",
            "target": channel,
            "command": "setlist",
            "data": response_daemon_data
        }

        api.request_async_threaded("POST", settings.MUSICDAEMON_URL, callback=None, data=response_daemon)

        return api.response_json(response, status.HTTP_202_ACCEPTED)


class QueueINAPI(RetrieveAPIView):
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(
        operation_summary="Add Music to PlayQueue",
        operation_description="Admin Only API",
        responses={'201': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, channel, track_id, *args, **kwargs):
        if channel not in SERVICE_CHANNEL:
            raise ValidationError(_("Invalid service channel"))

        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise ValidationError(_("Music does not exist"))

        PlayQueue(
            track=track,
            location=track.location,
            artist=track.artist,
            title=track.title,
            channel=channel
        ).save()

        api.request_async_threaded("POST", settings.MUSICDAEMON_URL, callback=None, data={
            "host": "server",
            "target": channel,
            "command": "queue",
            "data": {
                "id": track.id,
                "location": "/srv/media/%s" % track.location,
                "artist": track.artist,
                "title": track.title
            }
        })

        return api.response_json("OK", status.HTTP_201_CREATED)


class QueueOUTAPI(DestroyAPIView):
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(
        operation_summary="Delete Music from PlayQueue",
        operation_description="Admin Only API",
        responses={'202': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def delete(self, request, channel, index, *args, **kwargs):
        if channel not in SERVICE_CHANNEL:
            raise ValidationError(_("Invalid service channel"))

        try:
            queue = PlayQueue.objects.filter(channel__icontains=channel).order_by('id').distinct()[index]
        except IndexError:
            raise ValidationError(_("Out of index"))
        else:
            queue.delete()

        api.request_async_threaded("POST", settings.MUSICDAEMON_URL, callback=None, data={
            "host": "server",
            "target": channel,
            "command": "unqueue",
            "data": {
                "index_at": index
            }
        })

        return api.response_json("OK", status.HTTP_202_ACCEPTED)


class CallbackOnStartupAPI(RetrieveAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(
        operation_summary="Callback on_startup",
        operation_description="Public API",
        responses={'200': PlayQueueSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, channel, *args, **kwargs):
        if channel not in SERVICE_CHANNEL:
            raise ValidationError(_("Invalid service channel"))

        play_queue = PlayQueue.objects.filter(channel__icontains=channel)
        count_queue = play_queue.count()

        response = []
        if count_queue > 0:
            # Use pre exist queue
            for queue in play_queue:
                track = queue.track
                response.append({
                    "id": int(track.id),
                    "location": "/srv/media/%s" % track.location,
                    "artist": track.artist,
                    "title": track.title
                })
        else:
            # Select random track except for last played in 3 hours
            queue_tracks = get_random_track(channel, 8)

            # Set playlist
            for track in queue_tracks:
                serializer = PlayQueueSerializer(data={
                    "track_id": track.id,
                    "location": track.location,
                    "artist": track.artist,
                    "title": track.title
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()
                response.append({
                    "id": int(track.id),
                    "location": "/srv/media/%s" % track.location,
                    "artist": track.artist,
                    "title": track.title
                })

        return api.response_json_payload(response, status.HTTP_200_OK)


class CallbackOnPlayAPI(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = PlayQueueSerializer

    @swagger_auto_schema(
        operation_summary="Callback on_play",
        operation_description="Public API",
        responses={'200': "OK"})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, channel, *args, **kwargs):
        if channel not in SERVICE_CHANNEL:
            raise ValidationError(_("Invalid service channel"))

        try:
            track = Track.objects.get(id=request.data["id"])
        except Track.DoesNotExist:
            raise ValidationError(_("Music does not exist"))

        history = PlayHistorySerializer(data={
            "track_id": request.data["id"],
            "artist": request.data["artist"],
            "title": request.data["title"],
            "channel": channel,
            "played_at": now()
        })
        history.is_valid(raise_exception=True)
        history.save()

        track.last_played_at = now()
        track.play_count += 1
        track.save()

        return api.response_json("OK", status.HTTP_200_OK)


class CallbackOnStopAPI(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = PlayQueueSerializer

    @swagger_auto_schema(
        operation_summary="Callback on_stop",
        operation_description="Public API",
        responses={'200': PlayQueueSerializer})
    @transaction.atomic
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, channel, *args, **kwargs):
        if channel not in SERVICE_CHANNEL:
            raise ValidationError(_("Invalid service channel"))

        # Remove last played track from queue
        try:
            queue = PlayQueue.objects.filter(channel__icontains=channel).order_by('id').distinct()[0]
        except IndexError:
            raise ValidationError(_("Out of index"))
        else:
            queue.delete()

        # Select random track except for last played in 3 hours
        random_tracks = get_random_track(channel, 1)

        if len(random_tracks) > 0:
            # Add next track to queue at last
            next_track = random_tracks[0]
            serializer = PlayQueueSerializer(data={
                "track_id": next_track.id,
                "location": next_track.location,
                "artist": next_track.artist,
                "title": next_track.title
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return api.response_json_payload({
                "id": int(next_track.id),
                "location": "/srv/media/%s" % next_track.location,
                "artist": next_track.artist,
                "title": next_track.title
            }, status.HTTP_200_OK)
        else:
            return api.response_json_payload(None, status.HTTP_200_OK)
