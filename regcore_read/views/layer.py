from regcore import db
from regcore.responses import four_oh_four, success


def get(request, name, label_id, version):
    """Find and return the layer with this name + version + label"""
    layer = db.Layers().get(name, label_id, version)
    if layer is not None:
        return success(layer)
    else:
        return four_oh_four()
