from core import app
from core.responses import success, user_error
from flask import request
import jsonschema
from pyelasticsearch import ElasticSearch
import settings

REGULATION_SCHEMA = {
    'type': 'object',
    'id': 'reg_tree_node',
    'additionalProperties': False,
    'required': ['text', 'children', 'label'],
    'properties': {
        'text': {'type': 'string'},
        'children': {
            'type': 'array',
            'additionalItems': False,
            'items': {'$ref': 'reg_tree_node'}
        },
        'label': {
            'type': 'object', 
            'additionalProperties': False,
            'required': ['text', 'parts'],
            'properties': {
                'text': {'type': 'string'},
                'parts': {
                    'type': 'array', 
                    'additionalItems': False,
                    'items': {'type': 'string'}
                },
                'title': {'type': 'string'}
            }
        }
    }
}

@app.route('/regulation/<label>/<version>', methods=['PUT'])
def add(label, version):
    """Add this regulation node and all of its children to elastic search"""
    node = request.json

    try:
        jsonschema.validate(node, REGULATION_SCHEMA)
    except jsonschema.ValidationError, e:
        return user_error("JSON is invalid")

    if label != node['label']['text']:
        return user_error('label mismatch')

    to_save = []
    def add_node(node):
        node = dict(node)   #   copy
        node['version'] = version
        node['id'] = version + '/' + node['label']['text']
        to_save.append(node)
        for child in node['children']:
            add_node(child)
    add_node(node)

    es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)
    es.bulk_index(settings.ELASTIC_SEARCH_INDEX, 'reg_tree', to_save)

    return success()
