from flask import make_response
import json

def user_error(reason):
    """Silly user, you get a 400"""
    response = make_response(json.dumps({'reason': reason}), 400)
    response.headers['Content-type'] = 'application/json'
    return response

def success(ret_value=None):
    """Respond with either a JSON message or empty body"""
    if ret_value is not None:
        response = make_response(json.dumps(ret_value), 200)
        response.headers['Content-type'] = 'application/json'
    else:
        response = make_response('', 204)
    return response
