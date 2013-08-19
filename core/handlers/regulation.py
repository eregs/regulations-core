from collections import defaultdict

from flask import abort, Blueprint, request
import jsonschema
from pyelasticsearch import ElasticSearch

from core import db
from core.responses import success, user_error
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
            'type': 'array',
            'additionalItems': False,
            'items': {'type': 'string'}
        },
        'title': {'type': 'string'},
        'node_type': {'type': 'string'}
    }
}

blueprint = Blueprint('regulation', __name__)


@blueprint.route('/regulation/<label>', methods=['GET'])
def listing(label):
    """List versions of this regulation"""
    part = label.split('-')[0]
    notices = db.Notices().listing(label)
    by_date = defaultdict(list)
    for notice in (n for n in notices if 'effective_on' in n):
        by_date[notice['effective_on']].append(notice)
    reg_versions = set(db.Regulations().listing(label))

    regs = []
    for effective_date in sorted(by_date.keys(), reverse=True):
        notices = [(n['document_number'], n['effective_on']) 
                   for n in by_date[effective_date]]
        notices = sorted(notices, reverse=True)
        found_latest = False
        for version, effective in ((v,d) for v,d in notices 
                                   if v in reg_versions):
            if found_latest:
                regs.append({'version': version})
            else:
                found_latest = True
                regs.append({'version': version, 'by_date': effective})

    if regs:
        return success({'versions': regs})
    else:
        abort(404)


@blueprint.route('/regulation/<label>/<version>', methods=['PUT'])
def add(label, version):
    """Add this regulation node and all of its children to the db"""
    node = request.json

    try:
        jsonschema.validate(node, REGULATION_SCHEMA)
    except jsonschema.ValidationError, e:
        return user_error("JSON is invalid")

    if label != '-'.join(node['label']):
        return user_error('label mismatch')

    to_save = []
    def add_node(node):
        node = dict(node)   #   copy
        node['version'] = version
        node['label_string'] = '-'.join(node['label'])
        node['id'] = version + '/' + node['label_string']
        to_save.append(node)
        for child in node['children']:
            add_node(child)
    add_node(node)

    db.Regulations().bulk_put(to_save)

    return success()


@blueprint.route('/regulation/<label>/<version>', methods=['GET'])
def get(label, version):
    """Find and return the regulation with this version and label"""
    regulation = db.Regulations().get(label, version)
    if regulation:
        return success(regulation)
    else:
        abort(404)

