from collections import namedtuple
from functools import wraps

from webargs import fields, validate, ValidationError
from webargs.djangoparser import parser

from regcore.responses import user_error

MAX_PAGE_SIZE = 50

search_args = {
    'q': fields.Str(required=True),
    'version': fields.Str(missing=None),
    'regulation': fields.Str(missing=None),
    'is_root': fields.Bool(missing=None),
    'is_subpart': fields.Bool(missing=None),
    'page': fields.Int(missing=0),
    'page_size': fields.Int(missing=MAX_PAGE_SIZE,
                            validate=validate.Range(1, MAX_PAGE_SIZE)),
}
SearchArgs = namedtuple(
    'SearchArgs',
    ['q', 'version', 'regulation', 'is_root', 'is_subpart', 'page',
     'page_size'])


def requires_search_args(view):
    """Wraps a view in a validation test for search arguments. Passes the
    correctly-parsed SearchArgs through if there's no problem"""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            user_args = parser.parse(search_args, request)
        except ValidationError as err:
            return user_error(err.messages)
        return view(request, *args, search_args=SearchArgs(**user_args),
                    **kwargs)
    return wrapper
