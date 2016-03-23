from regcore.db import storage
from regcore.layer import standardize_params
from regcore.responses import four_oh_four, success


def get(request, name, doc_type, doc_id):
    """Find and return the layer with this name, referring to this doc_id"""
    params = standardize_params(doc_type, doc_id)
    layer = storage.for_layers.get(name, params.doc_type, params.doc_id)
    if layer is not None:
        return success(layer)
    else:
        return four_oh_four()
