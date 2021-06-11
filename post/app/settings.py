"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import json
from django.conf.locale.en import formats as en_formats
from google.oauth2 import service_account
import logging.config
from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_FILE = os.path.join(BASE_DIR, 'secret.json')

secret = json.loads(open(SECRET_FILE).read())


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret['SECRET_KEY']
JWT_SECRET_KEY = secret['JWT_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'rangefilter',
    'django_admin_listfilter_dropdown',
    'admin_numeric_filter',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'app',
    'accounts',
    'radio',
    'post',

    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'phonenumber_field',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'app.healthcheck_middleware.HealthCheckMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'drf_yasg.middleware.SwaggerExceptionMiddleware',
    'app.remove_next_middleware.RemoveNextMiddleware',
    'app.json404_middleware.JSON404Middleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'accounts', 'templates'),
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

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USERNAME'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT')
    },
}


# https://jupiny.com/2018/02/27/caching-using-redis-on-django/
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{0}:{1}/{2}".format(
            os.environ.get('REDIS_URL'), os.environ.get('REDIS_PORT'), os.environ.get('REDIS_DB')
        ),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
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

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_FORMAT = 'Y-m-d'

DATETIME_FORMAT = 'Y-m-d G:i:s'

DATE_INPUT_FORMATS = (
    '%Y-%m-%d',
)
TIME_INPUT_FORMATS = (
    '%H:%M:%S',
)
DATETIME_INPUT_FORMATS = (
    '%Y-%m-% %H:%M:%S',
)

en_formats.DATETIME_FORMAT = 'Y-m-d G:i:s.u'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# # Local storage
# STATIC_URL = '/static/'
# STATIC_DIR = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [
#     STATIC_DIR,
# ]
# STATIC_ROOT = os.path.join(BASE_DIR, '.static')

# Uncomment using cloud storage
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# https://blog.jun2.org/development/2019/07/23/django-security-options.html

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 63072000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
X_FRAME_OPTIONS = 'SAMEORIGIN'


HTTP_PROTOCOL = "http"
DOMAIN_URL = "127.0.0.1:8084"


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
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'accounts.backends.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'app.exceptions.core_exception_handler',
}

AUTHENTICATION_BACKENDS = (
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.JWTAuthentication',
)

JWT_VALID_HOUR = 36


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


################
# AWS S3 Setup #
################

# AWS_ACCESS_KEY_ID = config_secret_common['AWS_ACCESS_KEY_ID']
# AWS_SECRET_ACCESS_KEY = config_secret_common['AWS_SECRET_ACCESS_KEY']
#
# AWS_S3_REGION_NAME = 'ap-northeast-2'
# AWS_S3_SIGNATURE_VERSION = 's3v4'
#
# STATICFILES_LOCATION = 'static'
# STATICFILES_STORAGE = 'django_utils.storage_backend.s3_backend.StaticStorage'
# AWS_DEFAULT_ACL = None
# AWS_S3_ENCRYPTION = False
# DEFAULT_FILE_STORAGE = 'django_utils.storage_backend.s3_backend.MediaStorage'
# MEDIAFILES_LOCATION = 'media'

# AWS_STORAGE_BUCKET_NAME = 'api-prod-gloground-com'
#
# # STORAGE_DOMAIN = '%s.s3-accelerate.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# STORAGE_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME)
# STATIC_URL = "https://%s/%s/" % (STORAGE_DOMAIN, STATICFILES_LOCATION)


##############################
# Google Cloud Storage Setup #
##############################

GCP_PROJECT_ID = secret['GCP_PROJECT_ID']
GCP_STORAGE_BUCKET_NAME = secret['GCP_STORAGE_BUCKET_NAME']
GCP_SERVICE_ACCOUNT_JSON = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
GCP_USE_SERVICE_ACCOUNT_JSON = True

STORAGE_DOMAIN = "https://storage.cloud.google.com/%s" % GCP_STORAGE_BUCKET_NAME

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(GCP_SERVICE_ACCOUNT_JSON)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = secret['GS_BUCKET_NAME']

STATIC_URL = "https://storage.cloud.google.com/%s/" % GS_BUCKET_NAME


#####################
# File Upload Setup #
#####################

FILE_UPLOAD_PERMISSIONS = 0o777
FILE_UPLOAD_MAX_MEMORY_SIZE = 51200000
DATA_UPLOAD_MAX_MEMORY_SIZE = 51200000

STORAGE_DRIVER = "gcs"

FILE_UPLOAD_HANDLERS = (
    "radio.uploadhandler.ProgressBarUploadHandler",
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)


#############
# AES Setup #
#############

AES_KEY = secret['AES_KEY']
AES_SECRET = secret['AES_SECRET']


#################
# Account Setup #
#################

AUTH_DOMAIN_URL = "127.0.0.1:8081"
ACCOUNT_API_PATH = "/v1/user"
WWW_LANDING_URL = "127.0.0.1:8081"
ACCOUNT_LANDING_PATH = "/v1/user"
from accounts.email_setup import *


##############
# CORS Setup #
##############

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
