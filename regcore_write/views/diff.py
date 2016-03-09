from regcore.db import storage
from regcore.responses import success
from regcore_write.views.security import json_body, secure_write


@secure_write
@json_body
def add(request, label_id, old_version, new_version):
    """Add the diff to the db, indexed by the label and versions"""
    #   @todo: write a schema that verifies the diff's structure
    storage.for_diffs.put(
        label_id, old_version, new_version, request.json_body)
    return success()
