import json

from regcore.db import storage
from regcore.responses import success, user_error
from regcore_write.views.security import secure_write


@secure_write
def add(request, docnum):
    """Add the notice to the db"""
    try:
        notice = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeError):
        return user_error('invalid format')

    #   @todo: write a schema that verifies the notice's structure
    cfr_parts = notice.get('cfr_parts', [])
    if 'cfr_part' in notice:
        cfr_parts.append(notice['cfr_part'])
        del notice['cfr_part']
    notice['cfr_parts'] = cfr_parts

    storage.for_notices.put(docnum, notice)
    return success()
