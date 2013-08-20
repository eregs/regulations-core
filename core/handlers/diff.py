from core import db
from core.responses import success, user_error
from flask import abort, Blueprint, request

blueprint = Blueprint('diff', __name__)


@blueprint.route('/diff/<label>/<old_version>/<new_version>', methods=['PUT'])
def add(label, old_version, new_version):
    """Add the diff to the db, indexed by the label and versions"""
    diff = request.json

    if not diff:
        return user_error('invalid format')

    #   @todo: write a schema that verifies the diff's structure
    db.Diffs().put(label, old_version, new_version, diff)
    return success()


@blueprint.route('/diff/<label>/<old_version>/<new_version>', methods=['GET'])
def get(label, old_version, new_version):
    """Find and return the diff with the provided label / versions"""
    diff = db.Diffs().get(label, old_version, new_version)
    if diff:
        return success(diff)
    else:
        abort(404)
