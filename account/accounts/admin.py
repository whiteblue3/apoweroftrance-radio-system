from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_utils.input_filter import InputFilter
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import (
    User, Profile, AccessLog,
)
from .access_log import ACCESS_TYPE, ACCESS_STATUS


class StaffFilter(SimpleListFilter):
    title = 'Staff'
    parameter_name = 'is_staff'

    def lookups(self, request, model_admin):
        return (
            ("2", _('Super'),),
            ("1", _('Staff'),),
            ("0", _('Member'),),
        )

    def queryset(self, request, queryset):
        if self.value() == "2":
            return queryset.filter(Q(is_superuser=True))
        elif self.value() == "1":
            return queryset.filter(Q(is_staff=True))
        elif self.value() == "0":
            return queryset.filter(Q(is_staff=False))
        else:
            return queryset


class AccessTypeFilter(admin.SimpleListFilter):
    template = 'admin/dropdown_filter.html'

    parameter_name = 'access_type'
    title = _('Access Type')

    def lookups(self, request, model_admin):
        return ACCESS_TYPE

    def queryset(self, request, queryset):
        if self.value() is not None:
            access_type = [self.value()]
            return queryset.filter(
                Q(access_type__contains=access_type)
            )


class AccessStatusFilter(admin.SimpleListFilter):
    template = 'admin/dropdown_filter.html'

    parameter_name = 'access_status'
    title = _('Access Status')

    def lookups(self, request, model_admin):
        return ACCESS_STATUS

    def queryset(self, request, queryset):
        if self.value() is not None:
            access_status = [self.value()]
            return queryset.filter(
                Q(access_status__contains=access_status)
            )


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'created_at', 'last_login')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = (
        StaffFilter,
        ('created_at', DateRangeFilter), ('last_login', DateTimeRangeFilter),
    )
    ordering = ('-id',)
    inlines = [ProfileInline]

    def nickname(self, obj):
        try:
            # We use the `select_related` method to avoid making unnecessary
            # database calls.
            profile = Profile.objects.select_related('user').get(
                user__email=obj.email
            )
        except Profile.DoesNotExist:
            return ''
        if profile.nickname is None or profile.nickname is '':
            return ''
        else:
            return profile.nickname
    nickname.short_description = 'Nickname'

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if isinstance(inline, ProfileInline) and obj is None:
                continue
            yield inline.get_formset(request, obj), inline


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'ip_address', 'accessed_at',
        'request', 'access_type', 'access_status',
    ]
    search_fields = (
        'email', 'ip_address',
        'access_type', 'access_status',
        'request', 'request_body',
    )
    list_filter = (
        AccessTypeFilter, AccessStatusFilter,
        ('accessed_at', DateTimeRangeFilter),
    )
    ordering = ('-id',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
