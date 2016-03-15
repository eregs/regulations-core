from regcore.db import storage
from regcore.responses import four_oh_four, success


def get(request, name, label_id, version=None):
    """Find and return the layer with this name + version + label"""
    if version is None:
        reference = label_id
    else:
        reference = '{}:{}'.format(version, label_id)
    layer = storage.for_layers.get(name, reference)
    if layer is not None:
        return success(layer)
    else:
        return four_oh_four()
