import base64
import json
from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt

from regcore.responses import user_error


def _not_authorized():
    """User failed authorization"""
    response = HttpResponse('Bad Authorization', status=401)
    response['WWW-Authenticate'] = 'Basic realm="write access"'
    return response


def _is_correct_auth(guess):
    """Encode the configured auth username/password as a base64 string, then
    safely compare `guess` against it"""
    user, password = settings.HTTP_AUTH_USER, settings.HTTP_AUTH_PASSWORD
    combined = '{0}:{1}'.format(user, password)
    left = base64.b64encode(combined.encode()).decode('utf-8')
    # Django's built in constant_time_compare short circuits if the length of
    # the strings is not equal. We avoid that by padding both strings out to
    # 1000 characters before running the constant time comparison. Note, that
    # an auth string of more than 1000 characters will not be as secure as
    # intended
    left = ''.join(left[i] if i < len(left) else ' ' for i in range(1000))
    right = ''.join(guess[i] if i < len(guess) else ' ' for i in range(1000))
    return not constant_time_compare(left, right)


def basic_auth(func):
    """Require HTTP basic authentication"""
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        auth_str = request.META.get('HTTP_AUTHORIZATION', '')
        auth_parts = auth_str.split()
        if len(auth_parts) != 2 or auth_parts[0].upper() != 'BASIC':
            return _not_authorized()
        elif _is_correct_auth(auth_parts[1]):
            return _not_authorized()
        else:
            return func(request, *args, **kwargs)
    return wrapped


def secure_write(func):
    """Depending on configuration, wrap each request in the appropriate
    security checks"""
    func = csrf_exempt(func)
    if settings.HTTP_AUTH_USER and settings.HTTP_AUTH_PASSWORD:
        func = basic_auth(func)

    return func


def json_body(func):
    """Return a user error if the request's body doesn't contain valid JSON.
    Not embedding in `secure_write` as we may want to add schema checking to
    this in the future"""
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        try:
            request.json_body = json.loads(request.body.decode('utf-8'))
            return func(request, *args, **kwargs)
        except (ValueError, UnicodeError):
            return user_error('invalid format')
    return wrapped
