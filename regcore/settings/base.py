"""Base settings file; used by manage.py. All settings can be overridden via
local_settings.py"""
import os

from django.utils.crypto import get_random_string


INSTALLED_APPS = [
    'haystack',
    'regcore',
    'regcore_read',
    'regcore_write',
    'mptt',
]
MIDDLEWARE_CLASSES = []

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_string(50))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'eregs.db'
    }
}

TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'

ROOT_URLCONF = 'regcore.urls'

DEBUG = True

BACKENDS = {
    'regulations': 'regcore.db.django_models.DMRegulations',
    'layers': 'regcore.db.django_models.DMLayers',
    'notices': 'regcore.db.django_models.DMNotices',
    'diffs': 'regcore.db.django_models.DMDiffs'
}

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=regcore,regcore_read,regcore_write'
]

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

_envvars = ('HTTP_AUTH_USER', 'HTTP_AUTH_PASSWORD')
for var in _envvars:
    globals()[var] = os.environ.get(var)

try:
    from local_settings import *
except ImportError:
    pass
