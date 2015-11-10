import base64
from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import streql


def _not_authorized():
    """User failed authorization"""
    response = HttpResponse('Bad Authorization', status=401)
    response['WWW-Authenticate'] = 'Basic realm="write access"'
    return response


def _basic_auth_str():
    """Encode the configured auth username/password as a base64 string"""
    user, password = settings.HTTP_AUTH_USER, settings.HTTP_AUTH_PASSWORD
    combined = '{}:{}'.format(user, password)
    return base64.b64encode(combined)


def basic_auth(func):
    """Require HTTP basic authentication"""
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        auth_str = request.META.get('HTTP_AUTHORIZATION', '')
        auth_parts = auth_str.split()
        if len(auth_parts) != 2 or auth_parts[0].upper() != 'BASIC':
            return _not_authorized()
        # Note the use of a constant-time string comparison
        elif not streql.equals(auth_parts[1], _basic_auth_str()):
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
