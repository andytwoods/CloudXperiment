"""Production settings and globals."""


from os import environ
import sys

from .base import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)


ALLOWED_HOSTS = ['127.0.0.1', 'www.xpt.cloud', 'xpt.cloud', 'rpnwi8jsw0.execute-api.eu-west-1.amazonaws.com', 's3-eu-west-1.amazonaws.com']


MANDRILL_API_KEY = 'WsGrHDYxFF65hjS1m14tWQ'
DEFAULT_FROM_EMAIL = 'support@xpt.mobi'
#EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend'
EMAIL_BACKEND = 'django_ses_boto3.ses_email_backend.SESEmailBackend'
AWS_SES_REGION_NAME = 'eu-west-1'
AWS_SES_REGION_ENDPOINT = 'email.eu-west-1.amazonaws.com'
SERVER_EMAIL = 'andytwoods@gmail.com'
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    # identifier: xpt-zappa-db-id
    'default': {
        'ENGINE': 'zappa_django_utils.db.backends.s3sqlite',
        'NAME': 'sqlite.db',
        'BUCKET': 'your-db-bucket',
    }
}

########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
#SECRET_KEY = get_env_setting('SECRET_KEY')
SECRET_KEY = r"6=uean-9+-^kjcq26wn_t_4up!6sstp(h)tn)i6454kuy70l5k"
########## END SECRET CONFIGURATION


if ON_DEV_SERVER is False:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_HOST = True

AWS_S3_SECURE_URLS = True
AWS_QUERYSTRING_AUTH = False

LOGGING = {}

DEBUG = True

MIDDLEWARE += (
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'debug_panel.middleware.DebugPanelMiddleware',
)

CORS_ORIGIN_WHITELIST = ALLOWED_HOSTS + [AWS_BUCKET_LOCATION]
CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = "xptzappastatic"
AWS_DEFAULT_ACL = "public-read"
AWS_HEADERS = {
    "Expires": "Thu, 15 Apr 2010 20:00:00 GMT",
    "Cache-Control": "max-age=86400",
}

CLOUDFRONT_DOMAIN = "https://dcspglwlw0pwf.cloudfront.net"
CLOUDFRONT_ID = "E2CK3ARBEEECRK"
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'unique-snowflake',
    },
    # this cache backend will be used by django-debug-panel
    'debug-panel': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/debug-panel-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 200
        }
    }
}

if ON_DEV_SERVER:
    DEBUG = True
    CACHES['default'] = {'BACKEND': 'django.core.cache.backends.dummy.DummyCache', }
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': [],
                'class': 'django.utils.log.AdminEmailHandler'
            },

        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },

        }
    }
