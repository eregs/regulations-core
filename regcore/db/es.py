"""Each of the data structures relevant to the API (regulations, notices,
etc.), implemented using Elastic Search as a data store"""

from django.conf import settings
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from regcore.db import interface


class ESBase(object):
    """Shared code for Elastic Search storage models"""
    def __init__(self):
        self.es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)

    def safe_fetch(self, doc_type, id):
        """Attempt to retrieve a document from Elastic Search.
        :return: Found document, if it exists, otherwise None"""
        try:
            result = self.es.get(settings.ELASTIC_SEARCH_INDEX, doc_type, id)
            return result['_source']
        except ElasticHttpNotFoundError:
            return None


class ESRegulations(ESBase, interface.Regulations):
    """Implementation of Elastic Search as regulations backend"""
    def get(self, label, version):
        """Find the regulation label + version"""
        reg_node = self.safe_fetch('reg_tree', version + '/' + label)
        if reg_node is not None:
            del reg_node['regulation']
            del reg_node['version']
            del reg_node['label_string']
            del reg_node['id']
            return reg_node

    def _transform(self, reg, version):
        """Add some meta data fields which are ES specific"""
        node = dict(reg)    # copy
        node['version'] = version
        node['label_string'] = '-'.join(node['label'])
        node['regulation'] = node['label'][0]
        node['id'] = version + '/' + node['label_string']
        node['root'] = len(node['label']) == 1
        return node

    def bulk_put(self, regs, version, root_label):
        """Store all reg objects"""
        self.es.bulk_index(settings.ELASTIC_SEARCH_INDEX, 'reg_tree',
                           [self._transform(r, version) for r in regs])

    def listing(self, label=None):
        """List regulation version-label pairs that match this label (or are
        root, if label is None)"""
        if label is None:
            query = {'match': {'root': True}}
        else:
            query = {'match': {'label_string': label}}
        query = {'fields': ['label_string', 'version'], 'query': query}
        result = self.es.search(query, index=settings.ELASTIC_SEARCH_INDEX,
                                doc_type='reg_tree', size=100)
        return sorted((res['fields']['version'], res['fields']['label_string'])
                      for res in result['hits']['hits'])


class ESLayers(ESBase, interface.Layers):
    """Implementation of Elastic Search as layers backend"""
    def _transform(self, layer, layer_name, doc_type):
        """Add some meta data fields which are ES specific"""
        layer = dict(layer)     # copy
        doc_id = self.sanitize_doc_id(layer['doc_id'])
        del layer['doc_id']
        return {'id': ':'.join([layer_name, doc_type, doc_id]), 'layer': layer}

    def bulk_put(self, layers, layer_name, doc_type, root_doc_id):
        """Store all layer objects. Note this does not delete existing docs;
        it only replaces/inserts docs, which has loop holes"""
        self.es.bulk_index(
            settings.ELASTIC_SEARCH_INDEX, 'layer',
            [self._transform(l, layer_name, doc_type) for l in layers])

    def sanitize_doc_id(self, doc_id):
        return ':'.join(doc_id.split('/'))

    def get(self, name, doc_type, doc_id):
        """Find the layer that matches these parameters"""
        reference = ':'.join([name, doc_type, self.sanitize_doc_id(doc_id)])
        layer = self.safe_fetch('layer', reference)
        if layer is not None:
            return layer['layer']


class ESNotices(ESBase, interface.Notices):
    """Implementation of Elastic Search as notice backend"""
    def put(self, doc_number, notice):
        """Store a single notice"""
        self.es.index(settings.ELASTIC_SEARCH_INDEX, 'notice', notice,
                      id=doc_number)

    def get(self, doc_number):
        """Find the associated notice"""
        return self.safe_fetch('notice', doc_number)

    def listing(self, part=None):
        """All notices or filtered by cfr_part"""
        if part:
            query = {'match': {'cfr_parts': part}}
        else:
            query = {'match_all': {}}
        query = {'fields': ['effective_on', 'fr_url', 'publication_date'],
                 'query': query}
        notices = []
        results = self.es.search(query, doc_type='notice', size=100,
                                 index=settings.ELASTIC_SEARCH_INDEX)
        for notice in results['hits']['hits']:
            notice['fields']['document_number'] = notice['_id']
            notices.append(notice['fields'])
        return notices


class ESDiffs(ESBase, interface.Diffs):
    """Implementation of Elastic Search as diff backend"""
    @staticmethod
    def to_id(label, old, new):
        return "%s/%s/%s" % (label, old, new)

    def put(self, label, old_version, new_version, diff):
        """Store a diff between two versions of a regulation node"""
        struct = {
            'label': label,
            'old_version': old_version,
            'new_version': new_version,
            'diff': diff
        }
        self.es.index(settings.ELASTIC_SEARCH_INDEX, 'diff', struct,
                      id=self.to_id(label, old_version, new_version))

    def get(self, label, old_version, new_version):
        """Find the associated diff"""
        diff = self.safe_fetch('diff',
                               self.to_id(label, old_version, new_version))
        if diff is not None:
            return diff['diff']


class ESPreambles(ESBase, interface.Preambles):
    """Implementation of Elastic Search as preamble backend"""
    def put(self, doc_number, preamble):
        """Store a single preamble"""
        self.es.index(settings.ELASTIC_SEARCH_INDEX, 'preamble', preamble,
                      id=doc_number)

    def get(self, doc_number):
        """Find the associated preamble"""
        return self.safe_fetch('preamble', doc_number)
