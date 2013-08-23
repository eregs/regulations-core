import anyjson

from regcore import db
from regcore.responses import four_oh_four, success, user_error


def add(request, docnum):
    """Add the notice to the db"""
    try:
        notice = anyjson.deserialize(request.body)
    except ValueError:
        return user_error('invalid format')

    #   @todo: write a schema that verifies the notice's structure
    db.Notices().put(docnum, notice)
    return success()


def get(request, docnum):
    """Find and return the notice with this docnum"""
    notice = db.Notices().get(docnum)
    if notice:
        return success(notice)
    else:
        return four_oh_four()


def listing(request):
    """Find and return all notices"""
    return success({
        'results': db.Notices().listing(request.GET.get('part', None))
    })
