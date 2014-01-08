"""Each of the data structures relevant to the API (regulations, notices,
etc.), implemented as a 'split', writing content to both Django and Elastic
Search, but only reading from Django"""

from regcore.db.django_models import DMDiffs, DMLayers, DMNotices
from regcore.db.django_models import DMRegulations
from regcore.db.es import ESDiffs, ESLayers, ESNotices, ESRegulations


class SplitterRegulations(object):
    """Implementation of Django+Elastic Search as regulations backend"""
    def __init__(self):
        self.dm = DMRegulations()
        self.es = ESRegulations()

        self.get = self.dm.get
        self.listing = self.dm.listing

    def bulk_put(self, regs, version, root_label):
        """Write to both"""
        self.dm.bulk_put(regs, version, root_label)
        self.es.bulk_put(regs, version, root_label)


class SplitterLayers(object):
    """Implementation of Django+Elastic Search as layers backend"""
    def __init__(self):
        self.dm = DMLayers()
        self.es = ESLayers()

        self.get = self.dm.get

    def bulk_put(self, layers, version, layer_name, root_label):
        """Write to both"""
        self.dm.bulk_put(layers, version, layer_name, root_label)
        self.es.bulk_put(layers, version, layer_name, root_label)


class SplitterNotices(object):
    """Implementation of Django+Elastic Search as notices backend"""
    def __init__(self):
        self.dm = DMNotices()
        self.es = ESNotices()

        self.get = self.dm.get
        self.listing = self.dm.listing

    def put(self, doc_number, notice):
        """Write to both"""
        self.dm.put(doc_number, notice)
        self.es.put(doc_number, notice)


class SplitterDiffs(object):
    """Implementation of Django+Elastic Search as regulations backend"""
    def __init__(self):
        self.dm = DMDiffs()
        self.es = ESDiffs()

        self.get = self.dm.get

    def put(self, label, old_version, new_version, diff):
        """Write to both"""
        self.dm.put(label, old_version, new_version, diff)
        self.es.put(label, old_version, new_version, diff)
