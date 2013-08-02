from core import db
from core.responses import success, user_error
from flask import abort, Blueprint, request
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
            'type': 'array',
            'additionalItems': False,
            'items': {'type': 'string'}
        },
        'title': {'type': 'string'},
        'node_type': {'type': 'string'}
    }
}

blueprint = Blueprint('regulation', __name__)

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
        node['id'] = version + '/' + '-'.join(node['label'])
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

