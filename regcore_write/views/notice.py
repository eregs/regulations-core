from regcore.db import storage
from regcore.responses import success
from regcore_write.views.security import json_body, secure_write


@secure_write
@json_body
def add(request, docnum):
    """Add the notice to the db"""
    notice = request.json_body

    #   @todo: write a schema that verifies the notice's structure
    cfr_parts = notice.get('cfr_parts', [])
    if 'cfr_part' in notice:
        cfr_parts.append(notice['cfr_part'])
        del notice['cfr_part']
    notice['cfr_parts'] = cfr_parts

    storage.for_notices.put(docnum, notice)
    return success()
