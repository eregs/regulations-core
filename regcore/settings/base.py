"""Base settings file; used by manage.py. All settings can be overridden via
local_settings.py"""
import os

from django.utils.crypto import get_random_string


INSTALLED_APPS = [
    'mptt',
    'haystack',
    'regcore',
    'regcore_read',
    'regcore_write',
]
MIDDLEWARE_CLASSES = []

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_string(50))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'eregs.db'
    }
}

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]

ROOT_URLCONF = 'regcore.urls'

DEBUG = True

# Configurable storage backends, keyed by data_type (e.g. regulations, diffs)
# If a key is not set, defaults to regcore.db.django_models versions
BACKENDS = {}

ELASTIC_SEARCH_URLS = []
ELASTIC_SEARCH_INDEX = 'eregs'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'ERROR'
        }
    }
}

# Batch size used in `bulk_create`; defaults to a conservative value to avoid
# hitting SQLite limits
BATCH_SIZE = 50

_envvars = ('HTTP_AUTH_USER', 'HTTP_AUTH_PASSWORD')
for var in _envvars:
    globals()[var] = os.environ.get(var)

try:
    from local_settings import *
except ImportError:
    pass
