from core import app, db
from core.responses import success, user_error
from flask import request

@app.route('/notice/<doc_number>', methods=['PUT'])
def add(doc_number):
    """Add the notice to the db"""
    notice = request.json

    #   @todo: write a schema that verifies the notice's structure
    db.Notices().put(doc_number, notice)
    return success()

