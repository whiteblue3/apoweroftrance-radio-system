from django.db import models
from django_utils import multi_db_ralation


class ModelQuerySet(multi_db_ralation.ExternalDbQuerySetMixin, models.QuerySet):
    pass


class Config(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    key = models.CharField(blank=False, null=False, max_length=150)
    value = models.TextField(blank=False, null=False)

    comment = models.CharField(blank=False, null=False, max_length=150)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'system'
        verbose_name = 'Config'
        verbose_name_plural = 'Config'
