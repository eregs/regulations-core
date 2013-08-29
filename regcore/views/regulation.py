import anyjson
from collections import defaultdict

import jsonschema

from regcore import db
from regcore.responses import four_oh_four, success, user_error


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


def listing(request, label_id):
    """List versions of this regulation"""
    part = label_id.split('-')[0]
    notices = db.Notices().listing(label_id)
    by_date = defaultdict(list)
    for notice in (n for n in notices if 'effective_on' in n):
        by_date[notice['effective_on']].append(notice)
    reg_versions = set(db.Regulations().listing(label_id))

    regs = []
    for effective_date in sorted(by_date.keys(), reverse=True):
        notices = [(n['document_number'], n['effective_on'])
                   for n in by_date[effective_date]]
        notices = sorted(notices, reverse=True)
        found_latest = False
        for version, effective in ((v, d) for v, d in notices
                                   if v in reg_versions):
            if found_latest:
                regs.append({'version': version})
            else:
                found_latest = True
                regs.append({'version': version, 'by_date': effective})

    if regs:
        return success({'versions': regs})
    else:
        return four_oh_four()


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


def get(request, label_id, version):
    """Find and return the regulation with this version and label"""
    regulation = db.Regulations().get(label_id, version)
    if regulation:
        return success(regulation)
    else:
        return four_oh_four()
