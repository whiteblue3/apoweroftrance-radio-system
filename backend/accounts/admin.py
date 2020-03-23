from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    User, Profile, AccessLog,
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

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
