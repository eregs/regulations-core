from core import db
from core.responses import success, user_error
from flask import request, Blueprint

blueprint = Blueprint('notice', __name__)

@blueprint.route('/notice/<docnum>', methods=['PUT'])
def add(docnum):
    """Add the notice to the db"""
    notice = request.json

    if not notice:
        return user_error('invalid format')

    #   @todo: write a schema that verifies the notice's structure
    db.Notices().put(docnum, notice)
    return success()
