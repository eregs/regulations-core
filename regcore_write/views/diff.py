import json

from regcore import db
from regcore.responses import success, user_error
from regcore_write.views.security import secure_write


@secure_write
def add(request, label_id, old_version, new_version):
    """Add the diff to the db, indexed by the label and versions"""
    try:
        diff = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeError):
        return user_error('invalid format')

    #   @todo: write a schema that verifies the diff's structure
    db.Diffs().put(label_id, old_version, new_version, diff)
    return success()
