import logging

from regcore.db import storage
from regcore.layer import standardize_params
from regcore.responses import success, user_error
from regcore_write.views.security import json_body, secure_write

logger = logging.getLogger(__name__)


def child_label_of(lhs, rhs):
    """Is the lhs label a child of the rhs label"""
    #   Interpretations have a slightly different hierarchy
    if 'Interp' in lhs and 'Interp' in rhs:
        lhs_reg, lhs_comment = lhs.split('Interp')
        rhs_reg, rhs_comment = rhs.split('Interp')
        if lhs_reg.startswith(rhs_reg):
            return True

    #   Handle Interps with shared prefix as well as non-interps
    if lhs.startswith(rhs):
        return True

    return False


@secure_write
@json_body
def add(request, name, doc_type, doc_id):
    """Add the layer node and all of its children to the db"""
    layer = request.json_body
    if not isinstance(layer, dict):
        return user_error('invalid format')

    params = standardize_params(doc_type, doc_id)
    if params.doc_type not in ('preamble', 'cfr'):
        return user_error('invalid doc type')

    for key in layer.keys():
        # terms layer has a special attribute
        if not child_label_of(key, params.tree_id) and key != 'referenced':
            return user_error('label mismatch: {0}, {1}'.format(
                params.tree_id, key))

    storage.for_layers.bulk_delete(name, params.doc_type, params.doc_id)
    storage.for_layers.bulk_insert(child_layers(params, layer), name,
                                   params.doc_type)
    return success()


@secure_write
def delete(request, name, doc_type, doc_id):
    """Delete the layer node and all of its children from the db"""
    params = standardize_params(doc_type, doc_id)
    if params.doc_type not in ('preamble', 'cfr'):
        return user_error('invalid doc type')

    storage.for_layers.bulk_delete(name, params.doc_type, params.doc_id)
    return success()


def child_layers(layer_params, layer_data):
    """We are generally given a layer corresponding to an entire regulation.
    We need to split that layer up and store it per node within the
    regulation. If a reg has 100 nodes, but the layer only has 3 entries, it
    will still store 100 layer models -- many may be empty"""
    doc_id_components = layer_params.doc_id.split('/')
    if layer_params.doc_type == 'preamble':
        doc_tree = storage.for_documents.get('preamble', layer_params.doc_id)
    elif layer_params.doc_type == 'cfr':
        version, label = doc_id_components
        doc_tree = storage.for_documents.get('cfr', label, version)
    else:
        doc_tree = None
        logger.error("Invalid doc type: %s", layer_params.doc_type)
    if not doc_tree:
        return []

    to_save = []

    def find_labels(node):
        child_labels = []
        for child in node['children']:
            child_labels.extend(find_labels(child))

        label_id = '-'.join(node['label'])

        # Account for "{version}/{cfr_part}" the same as "{preamble id}"
        doc_id = '/'.join(doc_id_components[:-1] + [label_id])
        sub_layer = {'doc_id': doc_id}
        for key in layer_data:
            #   'referenced' is a special case of the definitions layer
            if key == label_id or key in child_labels or key == 'referenced':
                sub_layer[key] = layer_data[key]

        to_save.append(sub_layer)

        return child_labels + [label_id]

    find_labels(doc_tree)
    return to_save
