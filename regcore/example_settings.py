INSTALLED_APPS = [
    'regcore',
    'regcore_read',
    'regcore_write',
    'south'
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

SECRET_KEY = 'v^p)1cwc)%td*szt7lt-(nl=bf)k07t%65*t(mi1f!*18dz9m@'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'eregs.db'
    }
}

TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'

ROOT_URLCONF = 'regcore.read_write_urls'

DEBUG = True

BACKENDS = {
    'regulations': 'regcore.db.es.ESRegulations',
    'layers': 'regcore.db.es.ESLayers',
    'notices': 'regcore.db.es.ESNotices',
    'diffs': 'regcore.db.es.ESDiffs'
}

ELASTIC_SEARCH_URLS = []
ELASTIC_SEARCH_INDEX = 'eregs'

try:
    from local_settings import *
except ImportError:
    pass
