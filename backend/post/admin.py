from django.db.models import Q
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.admin.filters import (
    SimpleListFilter
)
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_utils.input_filter import InputFilter
from django.utils.translation import ugettext_lazy as _
from rangefilter.filter import DateTimeRangeFilter
from radio.models import Track
from .models import (
    CLAIM_CATEGORY, CLAIM_STATUS, CLAIM_STAFF_ACTION, NOTIFICATION_CATEGORY,
    Claim, ClaimReply, Comment, DirectMessage, Notification, NotificationUser
)


class ClaimCategoryFilter(SimpleListFilter):
    template = 'accounts/dropdown_filter.html'

    parameter_name = 'category'
    title = _('Category')

    def lookups(self, request, model_admin):
        return CLAIM_CATEGORY

    def queryset(self, request, queryset):
        if self.value() is not None:
            category = self.value()
            return queryset.filter(
                Q(category=category)
            )


class ClaimStatusFilter(SimpleListFilter):
    template = 'accounts/dropdown_filter.html'

    parameter_name = 'status'
    title = _('Status')

    def lookups(self, request, model_admin):
        return CLAIM_STATUS

    def queryset(self, request, queryset):
        if self.value() is not None:
            status = self.value()
            return queryset.filter(
                Q(status=status)
            )


class ClaimStaffActionFilter(SimpleListFilter):
    template = 'accounts/dropdown_filter.html'

    parameter_name = 'staff_action'
    title = _('Staff Action')

    def lookups(self, request, model_admin):
        return CLAIM_STAFF_ACTION

    def queryset(self, request, queryset):
        if self.value() is not None:
            staff_action = self.value()
            return queryset.filter(
                Q(staff_action=staff_action)
            )


class IssuerIDFilter(InputFilter):
    template = 'accounts/input_filter.html'

    parameter_name = 'issuer_id'
    title = _('Issuer ID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            issuer_id = self.value()
            return queryset.filter(
                Q(issuer_id=issuer_id)
            )


class AccepterIDFilter(InputFilter):
    template = 'accounts/input_filter.html'

    parameter_name = 'accepter_id'
    title = _('Accepter ID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            accepter_id = self.value()
            return queryset.filter(
                Q(accepter_id=accepter_id)
            )


class UserIDFilter(InputFilter):
    template = 'accounts/input_filter.html'

    parameter_name = 'user_id'
    title = _('User ID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            user_id = self.value()
            return queryset.filter(
                Q(user_id=user_id)
            )


class TrackIDFilter(InputFilter):
    template = 'accounts/input_filter.html'

    parameter_name = 'track_id'
    title = _('Track ID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            track_id = self.value()
            return queryset.filter(
                Q(track_id=track_id)
            )


class SendUserIDFilter(InputFilter):
    template = 'accounts/input_filter.html'

    parameter_name = 'send_user_id'
    title = _('Send User ID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            user_id = self.value()
            return queryset.filter(
                Q(send_user_id=user_id)
            )


class TargetUserIDFilter(InputFilter):
    template = 'accounts/input_filter.html'

    parameter_name = 'target_user_id'
    title = _('Target User ID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            user_id = self.value()
            return queryset.filter(
                Q(target_user_id=user_id)
            )


class NotificationCategoryFilter(SimpleListFilter):
    template = 'accounts/dropdown_filter.html'

    parameter_name = 'category'
    title = _('Category')

    def lookups(self, request, model_admin):
        return NOTIFICATION_CATEGORY

    def queryset(self, request, queryset):
        if self.value() is not None:
            category = self.value()
            return queryset.filter(
                Q(category=category)
            )


class ClaimReplyInline(admin.StackedInline):
    model = ClaimReply


class NotificationUserInline(admin.TabularInline):
    model = NotificationUser


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'category', 'status', 'staff_action', 'issuer_link', 'accepter_link',
        'issue', 'reason', 'track_link', 'user_link', 'created_at', 'updated_at',
    )
    search_fields = (
        'issue', 'reason',
        'issuer__email', 'issuer__nickname', 'issuer__mobile_number', 'issuer__first_name', 'issuer__last_name',
        'accepter__email', 'accepter__nickname', 'accepter__mobile_number', 'accepter__first_name', 'accepter__last_name',
        'user__email', 'user__nickname', 'user__mobile_number', 'user__first_name', 'user__last_name',
        'track__artist', 'track__title',
    )
    list_filter = (
        ClaimCategoryFilter, ClaimStatusFilter, ClaimStaffActionFilter, IssuerIDFilter, AccepterIDFilter, UserIDFilter, TrackIDFilter,
        ('created_at', DateTimeRangeFilter), ('updated_at', DateTimeRangeFilter),
    )
    ordering = ('-created_at',)
    inlines = (ClaimReplyInline,)

    def issuer_link(self, obj):
        User = get_user_model()
        user = User.objects.get(email=obj.issuer.email)
        url = reverse("admin:accounts_user_change", args=[user.id])
        link = '<a href="%s">%s</a>' % (url, obj.issuer.email)
        return mark_safe(link)
    issuer_link.short_description = 'Issuer'

    def accepter_link(self, obj):
        if obj.accepter is None:
            return ''
        else:
            User = get_user_model()
            user = User.objects.get(email=obj.accepter.email)
            url = reverse("admin:accounts_user_change", args=[user.id])
            link = '<a href="%s">%s</a>' % (url, obj.accepter.email)
            return mark_safe(link)
    accepter_link.short_description = 'Accepter'

    def user_link(self, obj):
        if obj.user is None:
            return ''
        else:
            User = get_user_model()
            user = User.objects.get(email=obj.user.email)
            url = reverse("admin:accounts_user_change", args=[user.id])
            link = '<a href="%s">%s</a>' % (url, obj.user.email)
            return mark_safe(link)
    user_link.short_description = 'User'

    def track_link(self, obj):
        if obj.track is None:
            return ''
        else:
            track = Track.objects.get(id=obj.track.id)
            url = reverse("admin:radio_track_change", args=[track.id])
            link = '<a href="%s">%s - %s</a>' % (url, obj.track.artist, obj.track.title)
            return mark_safe(link)
    track_link.short_description = 'Track'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'track_link', 'user_link', 'message', 'created_at', 'updated_at',
    )
    search_fields = (
        'message',
        'user__email', 'user__nickname', 'user__mobile_number', 'user__first_name', 'user__last_name',
        'track__artist', 'track__title',
    )
    list_filter = (
        UserIDFilter, TrackIDFilter, ('created_at', DateTimeRangeFilter), ('updated_at', DateTimeRangeFilter),
    )
    ordering = ('-created_at',)

    def user_link(self, obj):
        User = get_user_model()
        user = User.objects.get(email=obj.user.email)
        url = reverse("admin:accounts_user_change", args=[user.id])
        link = '<a href="%s">%s</a>' % (url, obj.user.email)
        return mark_safe(link)
    user_link.short_description = 'User'

    def track_link(self, obj):
        track = Track.objects.get(id=obj.track.id)
        url = reverse("admin:radio_track_change", args=[track.id])
        link = '<a href="%s">%s - %s</a>' % (url, obj.track.artist, obj.track.title)
        return mark_safe(link)
    track_link.short_description = 'Track'


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'send_user_link', 'target_user_link', 'message', 'created_at', 'updated_at',
    )
    search_fields = (
        'message',
        'send_user__email', 'send_user__nickname', 'send_user__mobile_number', 'send_user__first_name', 'send_user__last_name',
        'target_user__email', 'target_user__nickname', 'target_user__mobile_number', 'target_user__first_name', 'target_user__last_name',
    )
    list_filter = (
        SendUserIDFilter, TargetUserIDFilter, ('created_at', DateTimeRangeFilter), ('updated_at', DateTimeRangeFilter),
    )
    ordering = ('-created_at',)

    def send_user_link(self, obj):
        User = get_user_model()
        user = User.objects.get(email=obj.send_user.email)
        url = reverse("admin:accounts_user_change", args=[user.id])
        link = '<a href="%s">%s</a>' % (url, obj.send_user.email)
        return mark_safe(link)
    send_user_link.short_description = 'Send User'

    def target_user_link(self, obj):
        User = get_user_model()
        user = User.objects.get(email=obj.target_user.email)
        url = reverse("admin:accounts_user_change", args=[user.id])
        link = '<a href="%s">%s</a>' % (url, obj.target_user.email)
        return mark_safe(link)
    target_user_link.short_description = 'Target User'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'title', 'message', 'created_at',)
    search_fields = ('title', 'message',)
    list_filter = (NotificationCategoryFilter, ('created_at', DateTimeRangeFilter), 'targets',)
    ordering = ('-created_at',)
    inlines = (NotificationUserInline,)
