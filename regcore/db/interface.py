"""Interfaces for each of the storage systems."""
import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Regulations(object):
    @abc.abstractmethod
    def get(self, label, version):
        """Returns a regulation node or None"""
        raise NotImplementedError

    @abc.abstractmethod
    def bulk_put(self, regs, version, root_label):
        """Add many entries, with a root of root_label. Each should have the
        provided version"""
        raise NotImplementedError

    @abc.abstractmethod
    def listing(self, label=None):
        """Return a list of (version, label) pairs for regulation objects that
        match the provided label (or all root regs), sorted by version"""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class Layers(object):
    def bulk_put(self, layers, version, layer_name, root_label):
        """Add many entries, with the root of the entries having root_label
        and all entries having layer_name and version"""
        raise NotImplementedError

    def get(self, name, label, version):
        """Return a single layer (no meta data) or None"""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class Notices(object):
    def put(self, doc_number, notice):
        """:param str doc_number:
           :param dict notice:"""
        raise NotImplementedError

    def get(self, doc_number):
        """Return matching notice or None"""
        raise NotImplementedError

    def listing(self, part=None):
        """Return all notices or notices by part"""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class Diffs(object):
    def put(self, label, old_version, new_version, diff):
        """:param str label:
           :param str old_version:
           :param str new_version:
           :param dict diff:"""
        raise NotImplementedError

    def get(self, label, old_version, new_version):
        """Return matching diff or None"""
        raise NotImplementedError
