import logging

import jsonschema

from regcore.db import storage
from regcore.responses import success, user_error
from regcore_write.views.security import json_body, secure_write


#   This JSON schema is used to validate the regulation data provided
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


@secure_write
@json_body
def add(request, label_id, version):
    """Add this regulation node and all of its children to the db"""
    try:
        node = request.json_body
        jsonschema.validate(node, REGULATION_SCHEMA)
    except jsonschema.ValidationError:
        return user_error("JSON is invalid")

    if label_id != '-'.join(node['label']):
        return user_error('label mismatch')

    write_node(node, version, label_id)
    return success()


def write_node(node, version, label_id):

    to_save = []
    labels_seen = set()

    def add_node(node, parent=None):
        label_tuple = tuple(node['label'])
        if label_tuple in labels_seen:
            logging.warning("Repeat label: %s", label_tuple)
        labels_seen.add(label_tuple)

        node['parent'] = parent
        to_save.append(node)
        for child in node['children']:
            add_node(child, parent=node)
    add_node(node)

    storage.for_regulations.bulk_put(to_save, version, label_id)
