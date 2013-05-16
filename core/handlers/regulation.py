from core import app
from core.responses import success, user_error
from elasticutils import get_es
from flask import request
import jsonschema
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
            'items': [{'$ref': 'reg_tree_node'}]
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
                    'items': [{'type': 'string'}]
                },
                'title': {'type': 'string'}
            }
        }
    }
}

@app.route('/regulation/<label>/<version>', methods=['PUT'])
def add(label, version):
    node = request.json

    try:
        jsonschema.validate(node, REGULATION_SCHEMA)
    except jsonschema.ValidationError:
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

    es = get_es(settings.ELASTIC_SEARCH_URLS)
    es.bulk_index(settings.ELASTIC_SEARCH_INDEX, 'reg_tree', to_save)

    return success()
