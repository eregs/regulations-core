"""Helper functions for creating django HTTP responses"""


import anyjson
from django.http import Http404, HttpResponse


def user_error(reason):
    """Silly user, you get a 400"""
    obj = anyjson.serialize({'reason': reason})
    return HttpResponse(obj, 'application/json', 400)


def success(ret_value=None):
    """Respond with either a JSON message or empty body"""
    if ret_value is not None:
        return HttpResponse(anyjson.serialize(ret_value), 'application/json')
    else:
        return HttpResponse('', status=204)


def four_oh_four():
    """Layer of indirection for 404s. Allows easier migration between web
    frameworks"""
    raise Http404
