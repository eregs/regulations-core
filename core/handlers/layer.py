from core import db
from core.responses import success, user_error
from flask import Blueprint, request

blueprint = Blueprint('layer', __name__)

@blueprint.route('/layer/<name>/<label>/<version>', methods=['PUT'])
def add(name, label, version):
    """Add the layer node and all of its children to the db"""
    layer = request.json

    if not isinstance(layer, dict):
        return user_error('invalid format')

    keys = layer.keys() #   a stack
    keys.sort(reverse=True)
    for key in keys:
        if not key.startswith(label):
            return user_error('label mismatch: %s, %s' % (label, key))

    to_save = []
    while keys:
        key = keys.pop()
        sublayer = {key: layer[key]}
        # would be more efficient to step from the end, but this is > readable
        for k in [k for k in keys if k.startswith(key)]:
            sublayer[k] = layer[k]
        to_save.append({
            "id": version + "/" + name + "/" + key,
            "version": version,
            "name": name,
            "label": key,
            "layer": sublayer
        })

    db.Layers().bulk_put(to_save)

    return success()
