import os
import jwt
from datetime import datetime, timedelta
from calendar import timegm
from django.conf import settings
from rest_framework import authentication
from .error import (
    InvalidAuthentication, UserIsNotActive, UserDoesNotExist
)
from .models import User, JWTBlackList


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_setting_config(self):
        """local, dev, stage or prod"""
        return os.environ.get("DJANGO_SETTINGS")

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication.

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.

        2) `(user, token)` - We return a user/token combination when
                             authentication is successful.

                            If neither case is met, that means there's an error
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest.
        """
        if "/v1/user/authenticate" in request.get_full_path():
            is_access_from_login = True
        else:
            is_access_from_login = False

        request.user = None

        # `auth_header` should be an array with two elements: 1) the name of
        # the authentication header (in this case, "Token") and 2) the JWT
        # that we should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            # raise InvalidAuthentication
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            # raise InvalidAuthentication
            return None

        elif len(auth_header) > 2:
            # Invalid token header. The Token string should not contain spaces. Do
            # not attempt to authenticate.
            # raise InvalidAuthentication
            return None

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            # return None
            raise InvalidAuthentication

        # Check token is blacklist
        try:
            blacklist_token = JWTBlackList.objects.get(token=token)
        except JWTBlackList.DoesNotExist:
            pass
        else:
            raise InvalidAuthentication

        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self._authenticate_credentials_jwt(request, token, is_access_from_login)

    def _authenticate_credentials_jwt(self, request, token, is_access_from_login):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS512'])
        except:
            # msg = 'Invalid authentication. Could not decode token.'
            # raise exceptions.AuthenticationFailed(msg, code=401)
            raise InvalidAuthentication

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            # msg = 'No user matching this token was found.'
            # raise exceptions.AuthenticationFailed(msg)
            raise UserDoesNotExist

        if not user.is_active:
            # msg = 'This user has been deactivated.'
            # raise exceptions.AuthenticationFailed(msg)
            raise UserIsNotActive

        # Validate token expired
        orig_iat = payload.get('orig_iat')
        ip_address = payload.get('remote_ip', None)

        if ip_address is None:
            raise InvalidAuthentication

        if ip_address in self.get_client_ip(request):
            pass
        else:
            raise InvalidAuthentication

        if orig_iat:
            refresh_limit = timedelta(hours=settings.JWT_VALID_HOUR)
            refresh_limit = (refresh_limit.days * 24 * 3600 + refresh_limit.seconds)
            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                # msg = 'Token has expired.'
                # raise exceptions.AuthenticationFailed(msg)
                raise InvalidAuthentication

            if is_access_from_login:
                if "local" == self.get_setting_config() or "dev" == self.get_setting_config():
                    pass
                else:
                    from .serializers import JWTBlackListSerializer

                    expire_at = datetime.fromtimestamp(expiration_timestamp).strftime("%Y-%m-%dT%H:%M:%S")

                    old_token = JWTBlackListSerializer(data={
                        "email": user.email,
                        "token": token,
                        "ip_address": ip_address,
                        "expire_at": expire_at
                    })
                    old_token.is_valid(raise_exception=True)
                    old_token.save()

                # If token is still valid, refresh token
                (token, expire) = user._generate_jwt_token(orig_iat)

        return (user, token)
