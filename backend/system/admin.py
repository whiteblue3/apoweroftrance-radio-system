from django.contrib import admin
from .models import (
    Config
)


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'value', 'comment', 'created_at',)
    search_fields = ('key', 'value', 'comment',)
    ordering = ('-created_at',)
