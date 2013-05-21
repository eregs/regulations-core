ELASTIC_SEARCH_URLS = []
ELASTIC_SEARCH_INDEX = 'eregs'

try:
    from local_settings import *
except ImportError:
    pass
