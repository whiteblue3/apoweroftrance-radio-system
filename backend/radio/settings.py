"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import logging.config
from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@++f3cl$2c)f1m4_&0j$hjcnassuw7pd93oo5my)4w_fe41$c1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'radio',
    'accounts',

    'rest_framework',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'drf_yasg.middleware.SwaggerExceptionMiddleware',
    'radio.remove_next_middleware.RemoveNextMiddleware',
    'radio.json404_middleware.JSON404Middleware',
]

ROOT_URLCONF = 'radio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'radio.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': os.environ.get('DB_NAME'),
    #     'USER': os.environ.get('DB_USERNAME'),
    #     'PASSWORD': os.environ.get('DB_PASSWORD'),
    #     'HOST': os.environ.get('DB_HOST'),
    #     'PORT': os.environ.get('DB_PORT')
    # },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "radio",
        'USER': "whiteblue3",
        'PASSWORD': "",
        'HOST': "127.0.0.1",
        'PORT': 5432
    },
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ko-KR'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# # SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_HSTS_PRELOAD = True
# SECURE_HSTS_SECONDS = 63072000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# X_FRAME_OPTIONS = 'DENY'
# SESSION_COOKIE_SAMESITE = 'Strict'


# Disable Django's logging setup
LOGGING_CONFIG = None

LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        # 'file': {
        #             'level': 'INFO',
        #             'class': 'logging.handlers.TimedRotatingFileHandler',
        #             'filename': os.path.join('/var/log/uwsgi/app', 'django'),
        #             'when': 'D',  # this specifies the interval
        #             'interval': 1,  # defaults to 1, only necessary for other values
        #             'backupCount': 7,  # how many backup file to keep, 7 days
        #             'formatter': 'default',
        #         },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        # default for all undefined Python modules
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        # '': {
        #     'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        #     'handlers': ['console'],
        # },
        # # Our application code
        # 'app': {
        #     'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        #     # Avoid double logging because of root logger
        #     'propagate': False,
        # },
        # # Prevent noisy modules from logging to Sentry
        # 'noisy_module': {
        #     'level': 'ERROR',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})


##################
# JWT Auth Setup #
##################

AUTH_USER_MODEL = 'accounts.User'

# Configure the accounts in Django Rest Framework to be JWT
# http://www.django-rest-framework.org/
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.backends.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'radio.exceptions.core_exception_handler',
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.JWTAuthentication',
)


#################
# Swagger Setup #
#################

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
    },
}


AES_KEY = "BYOUwqYyMgWfEIjSHhmVHBoJgobVUJbR"
AES_SECRET = "I6V8HN5DMUPM4AES"


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = "hd2dj07@gmail.com"
EMAIL_HOST_PASSWORD = '"!Triace07"'
# EMAIL_USE_TLS = True
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
