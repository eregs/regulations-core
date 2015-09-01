import json
import os

import dj_database_url

from .base import *

DATABASES = {
    'default': dj_database_url.config()
}

vcap = json.loads(os.environ.get('VCAP_SERVICES', '{}'))
es_config = vcap.get('elasticsearch-swarm', [])
if es_config:
    HAYSTACK_CONNECTIONS['default'] = {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': es_config[0]['credentials']['uri'],
        'INDEX_NAME': 'eregs',
    }
