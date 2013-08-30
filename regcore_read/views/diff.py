from regcore import db
from regcore.responses import four_oh_four, success


def get(request, label_id, old_version, new_version):
    """Find and return the diff with the provided label / versions"""
    diff = db.Diffs().get(label_id, old_version, new_version)
    if diff:
        return success(diff)
    else:
        return four_oh_four()
