from core import db
from core.responses import success, user_error
from flask import abort, Blueprint, request

blueprint = Blueprint('layer', __name__)

@blueprint.route('/layer/<name>/<label>/<version>', methods=['PUT'])
def add(name, label, version):
    """Add the layer node and all of its children to the db"""
    layer = request.json

    if not isinstance(layer, dict):
        return user_error('invalid format')

    for key in layer.keys():
        # terms layer has a special attribute
        if not key.startswith(label) and key != 'referenced':
            return user_error('label mismatch: %s, %s' % (label, key))

    to_save = []
    for node_key in child_keys(label, version):
        sublayer = {}
        for layer_key in layer.keys():
            if layer_key.startswith(node_key):
                sublayer[layer_key] = layer[layer_key]

        to_save.append({
            "id": version + "/" + name + "/" + node_key,
            "version": version,
            "name": name,
            "label": node_key,
            "layer": sublayer
        })

    db.Layers().bulk_put(to_save)

    return success()

def child_keys(label, version):
    reg = db.Regulations().get(label, version)
    if not reg:
        return []

    keys = []
    def walk(node):
        keys.append(node['label']['text'])
        for child in node['children']:
            walk(child)
    walk(reg)
    return keys

@blueprint.route('/layer/<name>/<label>/<version>', methods=['GET'])
def get(name, label, version):
    """Find and return the layer with this name + version + label"""
    layer = db.Layers().get(name, label, version)
    if layer is not None:
        return success(layer)
    else:
        abort(404)
