import jwt
from calendar import timegm
from datetime import datetime, timedelta
from django.db import models
from django_utils import multi_db_ralation
from django.core.validators import EmailValidator, URLValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from .access_log import ACCESS_TYPE, ACCESS_STATUS


class ModelQuerySet(multi_db_ralation.ExternalDbQuerySetMixin, models.QuerySet):
    pass


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User`.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, email, first_name, last_name, password, is_business):
        """Create and return a `User` with an email, username and password."""
        if first_name is None:
            raise TypeError('Users must have an first_name.')

        if last_name is None:
            raise TypeError('Users must have an last_name.')

        if email is None:
            raise TypeError('Users must have an email address.')

        if password is None:
            raise TypeError('Staffusers must have a password.')

        user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.is_business = is_business
        user.save()

        return user

    def create_staffuser(self, email, first_name, last_name, password, is_business):
        """
        Create and return a `User` with staff (admin) permissions.
        """
        if password is None:
            raise TypeError('Staffusers must have a password.')

        user = self.create_user(email, first_name, last_name, password, is_business)
        user.is_superuser = False
        user.is_staff = True
        user.save()

        return user

    def create_superuser(self, email, first_name, last_name, password, is_business):
        """
        Create and return a `User` with superuser (super admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, first_name, last_name, password, is_business)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class TimestampedModel(models.Model):
    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        # By default, any model that inherits from `TimestampedModel` should
        # be ordered in reverse-chronological order. We can override this on a
        # per-model basis as needed, but reverse-chronological is a good
        # default ordering for most models.
        ordering = ['-created_at', '-updated_at']


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    # username = models.CharField(db_index=True, max_length=255, unique=False, default='')
    username = None

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True, validators=[EmailValidator])

    # When a user no longer wishes to use our platform, they may try to delete
    # their accounts. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. We
    # will simply offer users a way to deactivate their accounts instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users this flag will always be
    # false.
    is_staff = models.BooleanField(default=False)

    is_business = models.BooleanField(default=False)
    is_uploadable = models.BooleanField(default=False)

    # # A timestamp representing when this object was created.
    # created_at = models.DateTimeField(auto_now_add=True)
    #
    # # A timestamp reprensenting when this object was last updated.
    # updated_at = models.DateTimeField(auto_now=True)

    # More fields required by Django when specifying a custom user model.
    first_name = models.CharField(max_length=255, default='', blank=True)
    last_name = models.CharField(max_length=255, default='', blank=True)

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case we want it to be the email field.
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = 'User'
        verbose_name_plural = 'User'

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email

    def get_nickname(self):
        try:
            # We use the `select_related` method to avoid making unnecessary
            # database calls.
            profile = Profile.objects.select_related('user').get(
                user__email=self.email
            )
        except Profile.DoesNotExist:
            return ''
        if profile.nickname is not None and profile.nickname is not '':
            return profile.nickname
        else:
            return ''

    def get_username(self):
        return self.email

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return "{0}, {1}".format(self.first_name, self.last_name)

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.first_name

    # @property
    # def token(self):
    #     """
    #     Allows us to get a user's jwt_auth by calling `user.jwt_auth` instead of
    #     `user.generate_jwt_token().
    #
    #     The `@property` decorator above makes this possible. `jwt_auth` is called
    #     a "dynamic property".
    #     """
    #     return self._generate_jwt_token()

    def _generate_jwt_token(self, remote_ip, orig_iat=None):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(hours=settings.JWT_VALID_HOUR)

        payload = {
            'id': self.pk,
            'exp': int(dt.strftime('%s')),
            'remote_ip': remote_ip
        }

        if orig_iat is not None:
            payload['orig_iat'] = orig_iat
        else:
            payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
            )

        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS512')

        refresh_limit = timedelta(hours=settings.JWT_VALID_HOUR)
        refresh_limit = (refresh_limit.days * 24 * 3600 + refresh_limit.seconds)
        expiration_timestamp = payload['orig_iat'] + int(refresh_limit)

        try:
            jwtToken = token.decode('utf-8')
        except AttributeError:
            jwtToken = token

        return (jwtToken , expiration_timestamp)


class Profile(TimestampedModel):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    # There is an inherent relationship between the Profile and
    # User models. By creating a one-to-one relationship between the two, we
    # are formalizing this relationship. Every user will have one -- and only
    # one -- related Profile model.
    user = models.OneToOneField(
        'accounts.User', on_delete=models.CASCADE, db_index=True
    )

    nickname = models.CharField(blank=True, null=True, max_length=30)
    mobile_number = PhoneNumberField(blank=True, null=True)
    follow_count = models.IntegerField(default=0, null=False, blank=False)
    following_count = models.IntegerField(default=0, null=False, blank=False)

    # Each user profile will have a field where they can tell other users
    # something about themselves. This field will be empty when the user
    # creates their account, so we specify blank=True.
    bio = models.TextField(blank=True, null=True)

    # In addition to the `bio` field, each user may have a profile image or
    # avatar. This field is not required and it may be blank.
    image = models.CharField(blank=True, null=True, max_length=255)

    homepage = models.URLField(blank=True, null=True, validators=[URLValidator(schemes=['http', 'https'])])
    youtube = models.URLField(blank=True, null=True, validators=[URLValidator(schemes=['http', 'https'])])
    twitter = models.URLField(blank=True, null=True, validators=[URLValidator(schemes=['http', 'https'])])
    facebook = models.URLField(blank=True, null=True, validators=[URLValidator(schemes=['http', 'https'])])
    soundcloud = models.URLField(blank=True, null=True, validators=[URLValidator(schemes=['http', 'https'])])

    is_ban = models.BooleanField(default=False, null=False, blank=False)
    ban_reason = models.TextField(null=True, blank=True)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'accounts'
        external_db_fields = ['user']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profile'

    def __str__(self):
        return self.user.email


class Follow(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    user = models.ForeignKey(
        get_user_model(), related_name='Follow.user+', on_delete=models.CASCADE, null=False, blank=False, editable=False
    )

    follow_user = models.ForeignKey(
        get_user_model(), related_name='Follow.follow_user+', on_delete=models.CASCADE, null=False, blank=False, editable=False
    )

    follow = models.BooleanField(default=False, null=False, blank=False)

    updated_at = models.DateTimeField(auto_now_add=True, editable=False)

    objects = models.Manager.from_queryset(queryset_class=ModelQuerySet)()

    class Meta:
        app_label = 'accounts'
        external_db_fields = ['user', 'follow_user']
        verbose_name = 'Follow'
        verbose_name_plural = 'Follow'


class AccessLog(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    email = models.EmailField(db_index=True, blank=False, validators=[EmailValidator])

    ip_address = models.GenericIPAddressField(blank=False)

    # A timestamp representing when this object was created.
    accessed_at = models.DateTimeField(auto_now=True)

    request = models.CharField(max_length=255, blank=False, null=True, default=None)
    request_body = models.TextField(null=True, default=None)
    access_type = models.CharField(max_length=50, null=True, blank=False, default=None, choices=ACCESS_TYPE)
    access_status = models.CharField(max_length=50, null=True, blank=False, default=None, choices=ACCESS_STATUS)

    class Meta:
        app_label = 'accounts'
        verbose_name = 'Access Log'
        verbose_name_plural = 'Access Log'


class JWTBlackList(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)

    email = models.EmailField(db_index=True, blank=False, validators=[EmailValidator])
    token = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=False)
    expire_at = models.DateTimeField(db_index=True)
    accessed_at = models.DateTimeField(auto_now=True)
    log_ref = models.OneToOneField(
        'accounts.AccessLog', on_delete=models.CASCADE, default=None, null=True
    )

    class Meta:
        app_label = 'accounts'
        verbose_name = 'Black List'
        verbose_name_plural = 'Black List'
