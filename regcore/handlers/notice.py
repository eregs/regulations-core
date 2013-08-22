from regcore import db
from regcore.responses import success, user_error
from flask import abort, Blueprint, request

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

@blueprint.route('/notice/<docnum>', methods=['GET'])
def get(docnum):
    """Find and return the notice with this docnum"""
    notice = db.Notices().get(docnum)
    if notice:
        return success(notice)
    else:
        abort(404)

@blueprint.route('/notice', methods=['GET'])
def listing():
    """Find and return all notices"""
    return success({
        'results': db.Notices().listing(request.args.get('part', None))
    })
