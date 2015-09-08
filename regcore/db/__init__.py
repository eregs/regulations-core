"""Interfaces for each of the data structures relevant to the API
(regulations, notices, etc.). When instantiating the interface, it returns
the associated backend class instead (e.g. for Django, elastic search, or
the splitter backend)."""

from importlib import import_module

from django.conf import settings


def _select(key):
    module, class_name = settings.BACKENDS[key].rsplit('.', 1)
    module = import_module(module)
    return getattr(module, class_name)()


class Regulations(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return _select('regulations')

    def get(self, label, version):
        """Documentation method. Returns a regulation node or None"""
        raise NotImplementedError

    def bulk_put(self, regs, version, root_label):
        """Documentation method. Add many entries, with a root of root_label.
           Each should have the provided version"""
        raise NotImplementedError

    def listing(self, label=None):
        """Documentation method. Return a list of (version, label) pairs for
        regulation objects that match the provided label (or all root regs),
        sorted by version"""
        raise NotImplementedError


class Layers(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return _select('layers')

    def bulk_put(self, layers, version, layer_name, root_label):
        """Documentation method. Add many entries, with the root of the
        entries having root_label and all entries having layer_name and
        version"""
        raise NotImplementedError

    def get(self, name, label, version):
        """Doc method. Return a single layer (no meta data) or None"""
        raise NotImplementedError


class Notices(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return _select('notices')

    def put(self, doc_number, notice):
        """Documentation method. doc_number:String, notice:Dict"""
        raise NotImplementedError

    def get(self, doc_number):
        """Documentation method. Return matching notice or None"""
        raise NotImplementedError

    def listing(self, part=None):
        """Documentation method. Return all notices or notices by part"""
        raise NotImplementedError


class Diffs(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return _select('diffs')

    def put(self, label, old_version, new_version, diff):
        """Documentation method. label, old_version, new_version:String,
        diff:Dict"""
        raise NotImplementedError

    def get(self, label, old_version, new_version):
        """Documentation method. Return matching diff or None"""
        raise NotImplementedError
