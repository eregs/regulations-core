"""Schemas used by Elastic Search as well as an initialization function,
which sends the schemas over to the Elastic Search instance."""


from django.conf import settings
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import IndexAlreadyExistsError

NODE_SEARCH_SCHEMA = {
    'text': {'type': 'string'},  # Full text search
    #   Do not search children, but make them available
    'children': {'type': 'object', 'enabled': False},
    'label': {'type': 'string'},    # An array of strings
    'label_string': {'type': 'string', 'index': 'not_analyzed'},
    'regulation': {'type': 'string', 'index': 'not_analyzed'},
    'title': {'type': 'string'},
    'node_type': {'type': 'string', 'index': 'not_analyzed'},
    'id': {'type': 'string', 'index': 'not_analyzed'},
    'version': {'type': 'string', 'index': 'not_analyzed'}
}

LAYER_SCHEMA = {
    'id': {'type': 'string', 'index': 'not_analyzed'},
    #   i.e. doc_number
    'version': {'type': 'string', 'index': 'not_analyzed'},
    #   layer's name, e.g. "internal-citations"
    'name': {'type': 'string', 'index': 'not_analyzed'},
    #   label at which this layer applies (1005, 1005-12, 1005-12-b, etc.)
    'label': {'type': 'string', 'index': 'not_analyzed'},
    #   Will never search on the layer components
    'layer': {'type': 'object', 'enabled': False}
}

NOTICE_SCHEMA = {
    'id': {'type': 'string', 'index': 'not_analyzed'},
    #   Eventually, these fields will be searchable
    'notice': {'type': 'object', 'enabled': False}
}

DIFF_SCHEMA = {
    'id': {'type': 'string', 'index': 'not_analyzed'},
    'label': {'type': 'string', 'index': 'not_analyzed'},
    'old_version': {'type': 'string', 'index': 'not_analyzed'},
    'new_version': {'type': 'string', 'index': 'not_analyzed'},
    #   No need to index this
    'diff': {'type': 'object', 'enabled': False}
}


def init_schema():
    """Should be called at application startup. Makes sure the mappings and
    index exist."""
    es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)
    try:
        es.create_index(settings.ELASTIC_SEARCH_INDEX)
    except IndexAlreadyExistsError:
        pass

    #   Does not replace if exact mapping already exists
    es.put_mapping(settings.ELASTIC_SEARCH_INDEX, 'reg_tree', {
        'reg_tree': {'properties': NODE_SEARCH_SCHEMA}
    })
    es.put_mapping(settings.ELASTIC_SEARCH_INDEX, 'layer', {
        'layer': {'properties': LAYER_SCHEMA}
    })
    es.put_mapping(settings.ELASTIC_SEARCH_INDEX, 'notice', {
        'notice': {'properties': LAYER_SCHEMA}
    })
    es.put_mapping(settings.ELASTIC_SEARCH_INDEX, 'diff', {
        'diff': {'properties': DIFF_SCHEMA}
    })
