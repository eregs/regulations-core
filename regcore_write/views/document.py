import logging

import jsonschema

from regcore.db import storage
from regcore.responses import success, user_error
from regcore_write.views.security import json_body, secure_write

# This JSON schema is used to validate the regulation data provided
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
def add(request, doc_type, label_id, version=None):
    """Add this document node and all of its children to the db"""
    try:
        node = request.json_body
        jsonschema.validate(node, REGULATION_SCHEMA)
    except jsonschema.ValidationError:
        return user_error("JSON is invalid")

    if label_id != '-'.join(node['label']):
        return user_error('label mismatch')

    write_node(node, doc_type, label_id, version)
    return success()


def write_node(node, doc_type, label_id, version):

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

    storage.for_documents.bulk_delete(doc_type, label_id, version)
    storage.for_documents.bulk_insert(to_save, doc_type, version)


@secure_write
def delete(request, doc_type, label_id, version=None):
    """Delete this document node and all of its children from the db"""
    storage.for_documents.bulk_delete(doc_type, label_id, version)
    return success()
