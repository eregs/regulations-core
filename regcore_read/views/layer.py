from regcore.db import storage
from regcore.responses import four_oh_four, success


def get(request, name, label_id, version):
    """Find and return the layer with this name + version + label"""
    layer = storage.for_layers.get(name, '{}:{}'.format(version, label_id))
    if layer is not None:
        return success(layer)
    else:
        return four_oh_four()
