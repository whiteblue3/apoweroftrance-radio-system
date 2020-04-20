from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_utils.input_filter import InputFilter
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import Track, PlayHistory, CHANNEL

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
    list_display = (
        'id', 'user_link',
        'format', 'is_service',
        'channel', 'artist', 'title',
        'duration_field', 'play_count',
        'uploaded_at', 'last_played_at',
    )
    search_fields = (
        'title', 'artist',
    )
    list_filter = (
        UserFilter, ChannelFilter,
        ('uploaded_at', DateTimeRangeFilter), ('last_played_at', DateTimeRangeFilter),
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

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

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
