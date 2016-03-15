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
    def bulk_put(self, layers, layer_name, prefix):
        """Add multiple entries with the same layer_name.
        :param list[dict] layers: Each dictionary represents a layer; each
        should have a distinct "reference", which will be used during
        insertion.
        :param str layer_name: Identifier for this layer, e.g. "toc",
        "internal-citations", etc.
        :param str prefix: All layer entries with this prefix should be
        deleted before inserting"""
        raise NotImplementedError

    def get(self, name, reference):
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


@six.add_metaclass(abc.ABCMeta)
class Preambles(object):
    def put(self, doc_number, preamble):
        """:param str doc_number: unique identifier
           :param dict preamble: preamble data"""
        raise NotImplementedError

    def get(self, doc_number):
        """Return matching preamble or None"""
        raise NotImplementedError
