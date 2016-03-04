import json
import logging

import jsonschema

from regcore import db
from regcore.responses import success, user_error
from regcore_write.views.security import secure_write


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
def add(request, label_id, version):
    """Add this regulation node and all of its children to the db"""
    try:
        node = json.loads(request.body.decode('utf-8'))
        jsonschema.validate(node, REGULATION_SCHEMA)
    except (ValueError, UnicodeError):
        return user_error('invalid format')
    except jsonschema.ValidationError:
        return user_error("JSON is invalid")

    if label_id != '-'.join(node['label']):
        return user_error('label mismatch')

    to_save = []
    labels_seen = set()
    manager = db.Regulations()

    def add_node(node, parent=None):
        label_tuple = tuple(node['label'])
        if label_tuple in labels_seen:
            logging.warning("Repeat label: %s", label_tuple)
        labels_seen.add(label_tuple)

        node = dict(node, parent=parent)   # copy
        children = node.pop('children')
        row = manager._transform(node, version)
        row.parent = parent
        to_save.append(row)
        for child in children:
            add_node(child, parent=row)
    add_node(node)

    db.Regulations().bulk_put(to_save, version, label_id)

    return success()
