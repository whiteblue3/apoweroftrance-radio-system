This project is a part of [whiteblue3/apoweroftrance-radio](https://github.com/whiteblue3/apoweroftrance-radio) project

# How to packaging
    python3 setup.py sdist bdist_wheel

# Install
    pip3 install django-accounts
    
or

    pip3 install accounts-0.0.1.tar.gz


# Setup
in settings.py:

    INSTALLED_APPS = [
        ...
        
        'accounts',
        
        'rest_framework',
        'drf_yasg',
            
        ...
    ]

also configure with below

    MIDDLEWARE = [
    ...
    
        'drf_yasg.middleware.SwaggerExceptionMiddleware',
    
    ...
    ]
    
    
    AUTH_USER_MODEL = 'accounts.User'
    
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'accounts.backends.JWTAuthentication',
        ),
    }
    
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'accounts.backends.JWTAuthentication',
    )
    
    
    SWAGGER_SETTINGS = {
        'SECURITY_DEFINITIONS': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header'
            },
        },
    }
    
    
    AES_KEY = '...'
    AES_SECRET = '...'
    
    
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = "hd2dj07@gmail.com"
    EMAIL_HOST_PASSWORD = '"!Triace07"'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    
    
    ACCOUNT_AUTHENTICATION_METHOD = 'email'
    # ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS =1
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_UNIQUE_EMAIL = True
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    # ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    # ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
    # ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400 # 1 day in seconds
    # ACCOUNT_LOGOUT_REDIRECT_URL = '/'
    
    DOMAIN_URL = "127.0.0.1:8080"
    ACCOUNT_API_PATH = "/v1/user"
    
    RESET_PASSWORD_EMAIL_TITLE = "비밀번호 재설정 안내"
    RESET_PASSWORD_EMAIL_BODY = "임시 비밀번호: %s\n" \
                                "비밀번호 재설정하기: %s\n"
    RESET_PASSWORD_EMAIL_HTML = "<!DOCTYPE html><html lang='kr'><body>" \
                                "임시 비밀번호: %s<br />" \
                                "<a href='%s' target='_blank'>비밀번호 재설정하기</a><br />" \
                                "</body></html>"
    
    NOTIFY_SECURITY_ALERT_EMAIL_TITLE = "신규 로그인 알림"
    NOTIFY_SECURITY_ALERT_EMAIL_BODY = "새로운 디바이스에서 계정에 로그인되었습니다. 본인이 로그인한 것이 맞나요?\n" \
                                       "본인이 맞는 경우,\n" \
                                       "이 메시지를 무시하셔도 됩니다. 별도로 취해야 할 조치는 없습니다.\n\n" \
                                       "본인이 아닌 경우,\n" \
                                       "계정이 해킹되었을 수 있으며, 계정 보안을 위해 몇 가지 조치를 취해야 합니다. \n" \
                                       "조치를 취해주세요 -> %s\n" \
                                       "보다 안전한 조치를 위해 빠르게 임시비밀번호로 변경하시는 것이 좋습니다\n" \
                                       "비밀번호 변경: %s\n" \
                                       "위의 링크를 클릭하여 임시비밀번호로 변경하신 후에는 반드시 비밀번호를 원하는 비밀번호로 변경해주세요\n"
    NOTIFY_SECURITY_ALERT_EMAIL_HTML = "<!DOCTYPE html><html lang='kr'><body>" \
                                       "새로운 디바이스에서 계정에 로그인되었습니다. 본인이 로그인한 것이 맞나요?<br />" \
                                       "본인이 맞는 경우,<br />" \
                                       "이 메시지를 무시하셔도 됩니다. 별도로 취해야 할 조치는 없습니다.<br /><br />" \
                                       "본인이 아닌 경우,<br />" \
                                       "계정이 해킹되었을 수 있으며, 계정 보안을 위해 몇 가지 조치를 취해야 합니다. " \
                                       "시작하려면 지금 비밀번호를 재설정하세요.<br />" \
                                       "<a href='%s' target='_blank'>조치를 취해주세요</a><br /><br />" \
                                       "보다 안전한 조치를 위해 빠르게 임시비밀번호로 변경하시는 것이 좋습니다<br />" \
                                       "<a href='%s' target='_blank'>비밀번호 변경</a><br />" \
                                       "위의 링크를 클릭하여 임시비밀번호로 변경하신 후에는 반드시 비밀번호를 원하는 비밀번호로 변경해주세요<br />" \
                                       "</body></html>"



in urls.py:

    from django.contrib import admin
    from django.urls import path, re_path, include
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    
    schema_url_patterns = [
        ...
        path('v1/user/', include('accounts.urls', namespace='user')),
        ...
    ]
    
    schema_view = get_schema_view(
        openapi.Info(
            title="A Power of Trance Radio API",
            default_version='v1',
            description="사용법: 로그인 -> 리스폰스의 Token을 복사 -> 우상단의 Authorize클릭 -> Bearer <토큰> 입력후 Authorize클릭 -> 다른API 테스트"
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
        patterns=schema_url_patterns,
    )
    
    urlpatterns = [
        path('admin/', admin.site.urls),
    ] + schema_url_patterns
    
    urlpatterns += [
        re_path(r'^docs(?P<format>\.json|\.yaml)/$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
