import anyjson

import jsonschema

from regcore import db
from regcore.responses import success, user_error


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
            'type': 'array',
            'additionalItems': False,
            'items': {'type': 'string'}
        },
        'title': {'type': 'string'},
        'node_type': {'type': 'string'}
    }
}


def add(request, label_id, version):
    """Add this regulation node and all of its children to the db"""
    try:
        node = anyjson.deserialize(request.body)
        jsonschema.validate(node, REGULATION_SCHEMA)
    except ValueError:
        return user_error('invalid format')
    except jsonschema.ValidationError, e:
        return user_error("JSON is invalid")

    if label_id != '-'.join(node['label']):
        return user_error('label mismatch')

    to_save = []

    def add_node(node):
        node = dict(node)   # copy
        to_save.append(node)
        for child in node['children']:
            add_node(child)
    add_node(node)

    db.Regulations().bulk_put(to_save, version, label_id)

    return success()
