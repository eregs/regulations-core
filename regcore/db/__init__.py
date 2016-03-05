"""When instantiating a Regulations, Layers, etc., this will look up the
appropriate storage backend and create it"""
from importlib import import_module

from django.conf import settings


def _select(key):
    module, class_name = settings.BACKENDS[key].rsplit('.', 1)
    module = import_module(module)
    return getattr(module, class_name)()


class Regulations(object):
    def __new__(cls):
        return _select('regulations')


class Layers(object):
    def __new__(cls):
        return _select('layers')


class Notices(object):
    def __new__(cls):
        return _select('notices')


class Diffs(object):
    def __new__(cls):
        return _select('diffs')
