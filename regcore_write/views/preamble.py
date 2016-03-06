import json

from regcore.db import storage
from regcore.responses import success, user_error
from regcore_write.views.security import secure_write


@secure_write
def add(request, docnum):
    """Add the preamble to the db"""
    try:
        preamble = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeError):
        return user_error('invalid format')
    storage.for_preambles.put(docnum, preamble)
    return success()
