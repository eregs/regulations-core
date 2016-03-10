from regcore.db import storage
from regcore.responses import success
from regcore_write.views.security import json_body, secure_write


@secure_write
@json_body
def add(request, docnum):
    """Add the preamble to the db"""
    storage.for_preambles.put(docnum, request.json_body)
    return success()
