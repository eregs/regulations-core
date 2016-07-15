"""Interfaces for each of the storage systems."""
import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Documents(object):
    @abc.abstractmethod
    def get(self, doc_type, label, version):
        """Returns a regulation node or None"""
        raise NotImplementedError

    @abc.abstractmethod
    def bulk_delete(self, doc_type, root_label, version):
        """Delete all documents that match these parameters"""
        raise NotImplementedError

    @abc.abstractmethod
    def bulk_insert(self, regs, doc_type, version):
        """Add many entries, each with the provided version"""
        raise NotImplementedError

    @abc.abstractmethod
    def listing(self, doc_type, label=None):
        """Return a list of (version, label) pairs for regulation objects that
        match the provided label (or all root regs), sorted by version"""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class Layers(object):
    def bulk_delete(self, layer_name, doc_type, root_doc_id):
        """Deletes multiple entries with the same layer_name.
        :param str layer_name: Identifier for this layer, e.g. "toc",
        "internal-citations", etc.
        :param str doc_type: layers are keyed by doc_type
        :param str root_doc_id: the doc id of the "root" layer."""
        raise NotImplementedError

    def bulk_insert(self, layers, layer_name, doc_type):
        """Add multiple entries with the same layer_name.
        :param list[dict] layers: Each dictionary represents a layer; each
        should have a distinct "doc_id", which will be used during insertion.
        :param str layer_name: Identifier for this layer, e.g. "toc",
        "internal-citations", etc.
        :param str doc_type: layers are keyed by doc_type"""
        raise NotImplementedError

    def get(self, name, doc_type, doc_id):
        """Return a single layer (no meta data) or None"""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class Notices(object):
    def delete(self, doc_number):
        """:param str doc_number:"""
        raise NotImplementedError

    def insert(self, doc_number, notice):
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
    def delete(self, label, old_version, new_version):
        """:param str label:
           :param str old_version:
           :param str new_version:"""
        raise NotImplementedError

    def insert(self, label, old_version, new_version, diff):
        """:param str label:
           :param str old_version:
           :param str new_version:
           :param dict diff:"""
        raise NotImplementedError

    def get(self, label, old_version, new_version):
        """Return matching diff or None"""
        raise NotImplementedError
