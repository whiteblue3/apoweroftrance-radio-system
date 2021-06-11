from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from .models import User
from .access_log import *
from .util import accesslog


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(post_save, sender=User)
def create_related_profile(sender, instance, created, *args, **kwargs):
    # Notice that we're checking for `created` here. We only want to do this
    # the first time the `User` instance is created. If the save that caused
    # this signal to be run was an update action, we know the user already
    # has a profile.
    if instance and created:
        instance.profile = Profile.objects.create(user=instance)


@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
    ip = get_client_ip(request)
    accesslog(
        request, ACCESS_TYPE_AUTHENTICATE, ACCESS_STATUS_SUCCESSFUL,
        user.email, ip
    )


@receiver(user_logged_out)
def sig_user_logged_out(sender, user, request, **kwargs):
    ip = get_client_ip(request)
    accesslog(
        request, ACCESS_TYPE_LOGOUT, ACCESS_STATUS_SUCCESSFUL,
        user.email, ip
    )
