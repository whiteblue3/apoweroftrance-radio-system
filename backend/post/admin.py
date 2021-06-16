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
from accounts.models import User
from radio.models import Track
from .models import (
    CLAIM_CATEGORY, CLAIM_STATUS, Claim, ClaimReply, Comment
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


class ClaimReplyInline(admin.StackedInline):
    model = ClaimReply


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'category', 'status', 'issuer_link', 'accepter_link',
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
        ClaimCategoryFilter, ClaimStatusFilter, IssuerIDFilter, AccepterIDFilter, UserIDFilter, TrackIDFilter,
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
