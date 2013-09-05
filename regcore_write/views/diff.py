import anyjson
from django.views.decorators.csrf import csrf_exempt

from regcore import db
from regcore.responses import success, user_error


@csrf_exempt
def add(request, label_id, old_version, new_version):
    """Add the diff to the db, indexed by the label and versions"""
    try:
        diff = anyjson.deserialize(request.body)
    except ValueError:
        return user_error('invalid format')

    #   @todo: write a schema that verifies the diff's structure
    db.Diffs().put(label_id, old_version, new_version, diff)
    return success()
