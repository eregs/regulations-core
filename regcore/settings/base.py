"""Base settings file; used by manage.py. All settings can be overridden via
local_settings.py"""
import os

from django.utils.crypto import get_random_string


INSTALLED_APPS = [
    'haystack',
    'regcore',
    'regcore_read',
    'regcore_write',
    'south'
]

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
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:8983/solr'
    }
}

try:
    from local_settings import *
except ImportError:
    pass
