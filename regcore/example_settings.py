INSTALLED_APPS = [
    'regcore'
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

SECRET_KEY = 'v^p)1cwc)%td*szt7lt-(nl=bf)k07t%65*t(mi1f!*18dz9m@'

DATABASES = {}

TEST_RUNNER = 'testing.DatabaselessTestRunner'

ROOT_URLCONF = 'regcore.urls'

DEBUG = True

ELASTIC_SEARCH_URLS = []
ELASTIC_SEARCH_INDEX = 'eregs'

try:
    from local_settings import *
except ImportError:
    pass
