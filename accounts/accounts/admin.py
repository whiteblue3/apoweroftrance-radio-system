from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_utils.input_filter import InputFilter
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import (
    User, Profile, AccessLog,
)


class EmailFilter(InputFilter):
    parameter_name = 'email'
    title = _('EMail')

    def queryset(self, request, queryset):
        if self.value() is not None:
            email = self.value()
            return queryset.filter(
                Q(email__icontains=email)
            )


class FirstNameFilter(InputFilter):
    parameter_name = 'first_name'
    title = _('First Name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(first_name__icontains=name)
            )


class LastNameFilter(InputFilter):
    parameter_name = 'last_name'
    title = _('Last Name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(last_name__icontains=name)
            )


class UserFilter(InputFilter):
    parameter_name = 'user'
    title = _('User')

    def queryset(self, request, queryset):
        if self.value() is not None:
            email = self.value()
            return queryset.filter(
                Q(user__email__icontains=email)
            )


class IPAddressFilter(InputFilter):
    parameter_name = 'ip_address'
    title = _('IP Address')

    def queryset(self, request, queryset):
        if self.value() is not None:
            ip_address = self.value()
            return queryset.filter(
                Q(ip_address__icontains=ip_address)
            )


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        # (_('Personal info'), {'fields': ('first_name', 'last_name')}),
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
        EmailFilter, FirstNameFilter, LastNameFilter,
        ('created_at', DateRangeFilter), ('last_login', DateTimeRangeFilter),
    )
    ordering = ('-created_at',)
    inlines = [ProfileInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            user = request.user
            if user.is_superuser:
                self.fieldsets = (
                    (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
                    # (_('Personal info'), {'fields': ('first_name', 'last_name')}),
                    (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                                   'groups', 'user_permissions')}),
                )
            else:
                self.fieldsets = (
                    (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
                    # (_('Personal info'), {'fields': ('first_name', 'last_name')}),
                    (_('Permissions'), {'fields': ('is_active', 'groups', 'user_permissions',)}),
                )
        return True

    def has_module_permission(self, request):
        return True


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
        EmailFilter, IPAddressFilter
    )
    ordering = ('-accessed_at',)

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
