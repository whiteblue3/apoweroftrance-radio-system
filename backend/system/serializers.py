from datetime import datetime
from dateutil.tz import tzlocal
from rest_framework import serializers
from .models import (
    Config
)


class ConfigSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    key = serializers.CharField(allow_null=False, allow_blank=False, max_length=150)
    value = serializers.CharField(allow_null=False, allow_blank=False, max_length=3000)

    comment = serializers.CharField(allow_null=False, allow_blank=False, max_length=150)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Config
        fields = (
            'id',
            'key', 'value', 'comment',
            'created_at', 'updated_at',
        )
