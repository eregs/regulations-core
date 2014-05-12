import anyjson
from django.views.decorators.csrf import csrf_exempt

from regcore import db
from regcore.responses import success, user_error


@csrf_exempt
def add(request, docnum):
    """Add the notice to the db"""
    try:
        notice = anyjson.deserialize(request.body)
    except ValueError:
        return user_error('invalid format')

    #   @todo: write a schema that verifies the notice's structure
    cfr_parts = notice.get('cfr_parts', [])
    if 'cfr_part' in notice:
        cfr_parts.append(notice['cfr_part'])
        del notice['cfr_part']
    notice['cfr_parts'] = cfr_parts

    db.Notices().put(docnum, notice)
    return success()
