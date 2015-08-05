import dj_database_url

from .base import *

DATABASES = {
    'default': dj_database_url.config()
}
# @todo: Search
