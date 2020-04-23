from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages import ERROR
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, re_path
from django.utils.safestring import mark_safe
from django_utils.input_filter import InputFilter
from rest_framework.exceptions import ValidationError
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import Track, PlayHistory, CHANNEL
from .util import get_redis_data, set_redis_data, delete_track
from django_utils import api

"""
Track admin
- 일괄 업로드

PlayQueue admin
- 플레이리스트 리셋
- 큐인
- 큐아웃
- 데몬과 플레이리스트 싱크 맞추기
"""


class UserFilter(InputFilter):
    parameter_name = 'user__email'
    title = _('User')

    def queryset(self, request, queryset):
        if self.value() is not None:
            email = self.value()
            return queryset.filter(
                Q(user__email__icontains=email)
            )


class ChannelFilter(admin.SimpleListFilter):
    template = 'admin/dropdown_filter.html'

    parameter_name = 'channel'
    title = _('Service Channel')

    def lookups(self, request, model_admin):
        return CHANNEL

    def queryset(self, request, queryset):
        if self.value() is not None:
            channel = [self.value()]
            return queryset.filter(
                Q(channel__contains=channel)
            )


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    change_list_template = "admin/track_list.html"

    list_display = (
        'id', 'user_link',
        'format', 'is_service',
        'channel', 'artist', 'title',
        'duration_field',
        'play_count',
        'queue_in_playlist', 'queue_out_playlist',
        'uploaded_at', 'updated_at', 'last_played_at',
    )
    search_fields = (
        'title', 'artist',
    )
    list_filter = (
        UserFilter, ChannelFilter,
        ('uploaded_at', DateTimeRangeFilter), ('updated_at', DateTimeRangeFilter), ('last_played_at', DateTimeRangeFilter),
    )
    ordering = ('-id',)

    def user_link(self, obj):
        User = get_user_model()
        user = User.objects.get(email=obj.user.email)
        url = reverse("admin:accounts_user_change", args=[user.id])
        link = '<a href="%s">%s</a>' % (url, obj.user.email)
        return mark_safe(link)
    user_link.short_description = 'User'

    def duration_field(self, obj):
        return obj.duration.strftime("%H:%M:%S.%f")
    duration_field.admin_order_field = 'duration'
    duration_field.short_description = 'Duration'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['channels'] = CHANNEL
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<track_id>.+)/(?P<channel>.+)/queuein$',
                self.admin_site.admin_view(self.process_queuein),
                name='track-queuein',
            ),
            re_path(
                r'^(?P<track_id>.+)/(?P<channel>.+)/queueout$',
                self.admin_site.admin_view(self.process_queueout),
                name='track-queueout',
            ),
        ]
        return custom_urls + urls

    def process_queuein(self, request, track_id, channel, *args, **kwargs):
        redis_data = get_redis_data(channel)
        if not redis_data:
            self.message_user(request, 'Channel does not exist', level=ERROR)
        else:
            playlist = redis_data["playlist"]

            track = Track.objects.get(id=track_id)

            new_track = {
                "id": track.id,
                "location": "/srv/media/%s" % track.location,
                "artist": track.artist,
                "title": track.title
            }

            playlist.append(new_track)
            set_redis_data(channel, "playlist", playlist)

            api.request_async_threaded("POST", settings.MUSICDAEMON_URL, callback=None, data={
                "host": "server",
                "target": channel,
                "command": "setlist",
                "data": playlist
            })

            self.message_user(request, 'Success')

        url = reverse(
            'admin:radio_track_changelist',
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def process_queueout(self, request, track_id, channel, *args, **kwargs):
        redis_data = get_redis_data(channel)
        if not redis_data:
            self.message_user(request, 'Channel does not exist', level=ERROR)
        else:
            playlist = redis_data["playlist"]

            track = Track.objects.get(id=track_id)

            index = None
            for music in playlist:
                if int(music["id"]) == int(track.id):
                    index = playlist.index(music)
                    break

            if index is None:
                self.message_user(request, 'Out of Index', level=ERROR)
            else:
                playlist.pop(index)

                set_redis_data(channel, "playlist", playlist)
                api.request_async_threaded("POST", settings.MUSICDAEMON_URL, callback=None, data={
                    "host": "server",
                    "target": channel,
                    "command": "setlist",
                    "data": playlist
                })

                self.message_user(request, 'Success')

        url = reverse(
            'admin:radio_track_changelist',
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def queue_in_playlist(self, obj):
        html = ''
        args = []
        for in_service_channel, in_service_channel_name in CHANNEL:
            html += '<a class="button" href="{}">%s</a>&nbsp;' % in_service_channel_name
            args.append(
                reverse('admin:track-queuein', args=[obj.pk, in_service_channel]),
            )
        return format_html(html, *args)
    queue_in_playlist.short_description = 'Queue In'
    queue_in_playlist.allow_tags = True

    def queue_out_playlist(self, obj):
        html = ''
        args = []
        for in_service_channel, in_service_channel_name in CHANNEL:
            html += '<a class="button" href="{}">%s</a>&nbsp;' % in_service_channel_name
            args.append(
                reverse('admin:track-queueout', args=[obj.pk, in_service_channel]),
            )
        return format_html(html, *args)
    queue_out_playlist.short_description = 'Queue Out'
    queue_out_playlist.allow_tags = True

    def delete_queryset(self, request, queryset):
        print('========================delete_queryset========================')
        print(queryset)

        """
        you can do anything here BEFORE deleting the object(s)
        """

        try:
            for track in queryset:
                delete_track(track)
        except ValidationError as e:
            self.message_user(request, e.detail, level=ERROR)
        else:
            self.message_user(request, "Success")

        """
        you can do anything here AFTER deleting the object(s)
        """

        print('========================delete_queryset========================')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True


class TrackInline(admin.StackedInline):
    model = Track
    can_delete = False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True


@admin.register(PlayHistory)
class PlayHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'track_link', 'channel', 'artist', 'title', 'played_at',
    )
    search_fields = (
        'artist', 'title'
    )
    list_filter = (
        ChannelFilter,
    )
    ordering = ('-played_at',)

    def track_link(self, obj):
        track = Track.objects.get(id=obj.track.id)
        url = reverse("admin:radio_track_change", args=[track.id])
        link = '<a href="%s">%s</a>' % (url, obj.track.id)
        return mark_safe(link)
    track_link.short_description = 'Track'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True
