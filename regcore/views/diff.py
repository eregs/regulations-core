import anyjson

from regcore import db
from regcore.responses import four_oh_four, success, user_error


def add(request, label_id, old_version, new_version):
    """Add the diff to the db, indexed by the label and versions"""
    try:
        diff = anyjson.deserialize(request.body)
    except ValueError:
        return user_error('invalid format')

    #   @todo: write a schema that verifies the diff's structure
    db.Diffs().put(label_id, old_version, new_version, diff)
    return success()


def get(request, label_id, old_version, new_version):
    """Find and return the diff with the provided label / versions"""
    diff = db.Diffs().get(label_id, old_version, new_version)
    if diff:
        return success(diff)
    else:
        return four_oh_four()
