import json

from regcore.db import storage
from regcore.responses import success, user_error
from regcore_write.views.security import secure_write
from regcore.db.django_models import get_adjacency_map
from regcore.models import Regulation


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
def add(request, name, label_id, version):
    """Add the layer node and all of its children to the db"""
    try:
        layer = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeError):
        return user_error('invalid format')

    if not isinstance(layer, dict):
        return user_error('invalid format')

    for key in layer.keys():
        # terms layer has a special attribute
        if not child_label_of(key, label_id) and key != 'referenced':
            return user_error('label mismatch: %s, %s' % (label_id, key))

    storage.for_layers.bulk_put(
        child_layers(name, label_id, version, layer), version, name, label_id)

    return success()


def child_layers(layer_name, root_label, version, root_layer):
    """We are generally given a layer corresponding to an entire regulation.
    We need to split that layer up and store it per node within the
    regulation. If a reg has 100 nodes, but the layer only has 3 entries, it
    will still store 100 layer models -- many may be empty"""
    regs = Regulation.objects.filter(
        label_string=root_label,
        version=version,
    ).get_descendants(
        include_self=True,
    )
    regs = list(regs)

    if not regs:
        return []

    adjacency_map = get_adjacency_map(regs)
    to_save = []

    def find_labels(node):
        child_labels = []
        for child in adjacency_map.get(node.id, []):
            child_labels.extend(find_labels(child))

        sub_layer = {'label': node.label_string}
        for key in root_layer:
            # 'referenced' is a special case of the definitions layer
            if key in [node.label_string, 'referenced'] or key in child_labels:
                sub_layer[key] = root_layer[key]

        to_save.append(sub_layer)

        return child_labels + [node.label_string]

    find_labels(regs[0])

    return to_save
