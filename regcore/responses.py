from flask import jsonify, make_response
import json

def user_error(reason):
    """Silly user, you get a 400"""
    response = jsonify(reason=reason)
    response.status_code = 400
    return response

def success(ret_value=None):
    """Respond with either a JSON message or empty body"""
    if ret_value is not None:
        response = jsonify(ret_value)
    else:
        response = make_response('', 204)
    return response
