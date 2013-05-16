from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import IndexAlreadyExistsError
import settings

NODE_SEARCH_SCHEMA = {
    'text': {'type': 'string'}, #   Full text search
    #   Do not search children, but make them available
    'children': {'type': 'object', 'enabled': False},
    'label': {'type': 'object', 'properties': {
        #   Exact match
        'text': {'type': 'string', 'index': 'not_analyzed'},
        'parts': {'type': 'string', 'index': 'not_analyzed'},
        'title': {'type': 'string'}
    }},
    'id': {'type': 'string', 'index': 'not_analyzed'},
    'version': {'type': 'string', 'index': 'not_analyzed'}
}


def init_schema():
    es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)
    try:
        es.create_index(settings.ELASTIC_SEARCH_INDEX)
    except IndexAlreadyExistsError:
        pass

    #   Does not replace if exact mapping already exists
    es.put_mapping(settings.ELASTIC_SEARCH_INDEX, 'reg_tree', {
        'reg_tree': {'properties': NODE_SEARCH_SCHEMA}
    })
