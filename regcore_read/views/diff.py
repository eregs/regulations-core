from regcore.db import storage
from regcore.responses import four_oh_four, success


def get(request, label_id, old_version, new_version):
    """Find and return the diff with the provided label / versions"""
    diff = storage.for_diffs.get(label_id, old_version, new_version)
    if diff is not None:
        return success(diff)
    else:
        return four_oh_four()
