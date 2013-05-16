from flask import make_response
import json

def user_error(reason):
    response = make_response(json.dumps({'reason': reason}), 400)
    response.headers['Content-type'] = 'application/json'
    return response

def success(ret_value=None):
    if ret_value is not None:
        response = make_response(json.dumps(ret_value), 200)
    else:
        response = make_response('', 204)
    return response
