import anyjson
from django.views.decorators.csrf import csrf_exempt

from regcore import db
from regcore.responses import success, user_error


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


@csrf_exempt
def add(request, name, label_id, version):
    """Add the layer node and all of its children to the db"""
    try:
        layer = anyjson.deserialize(request.body)
    except ValueError:
        return user_error('invalid format')

    if not isinstance(layer, dict):
        return user_error('invalid format')

    for key in layer.keys():
        # terms layer has a special attribute
        if not child_label_of(key, label_id) and key != 'referenced':
            return user_error('label mismatch: %s, %s' % (label_id, key))

    db.Layers().bulk_put(child_layers(name, label_id, version, layer),
                         version, name, label_id)

    return success()


def child_layers(layer_name, root_label, version, root_layer):
    """We are generally given a layer corresponding to an entire regulation.
    We need to split that layer up and store it per node within the
    regulation. If a reg has 100 nodes, but the layer only has 3 entries, it
    will still store 100 layer models -- many may be empty"""
    root = db.Regulations().get(root_label, version)
    if not root:
        return []

    to_save = []

    def find_labels(node):
        child_labels = []
        for child in node['children']:
            child_labels.extend(find_labels(child))

        label_id = '-'.join(node['label'])

        sub_layer = {'label': label_id}
        for key in root_layer:
            #   'referenced' is a special case of the definitions layer
            if key == label_id or key in child_labels or key == 'referenced':
                sub_layer[key] = root_layer[key]

        to_save.append(sub_layer)

        return child_labels + [label_id]

    find_labels(root)
    return to_save
