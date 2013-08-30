import anyjson

from regcore import db
from regcore.responses import success, user_error


def add(request, docnum):
    """Add the notice to the db"""
    try:
        notice = anyjson.deserialize(request.body)
    except ValueError:
        return user_error('invalid format')

    #   @todo: write a schema that verifies the notice's structure
    db.Notices().put(docnum, notice)
    return success()
