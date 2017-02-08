"""Each of the data structures relevant to the API (regulations, notices,
etc.), implemented using Elastic Search as a data store"""
import logging

from django.conf import settings
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from regcore.db import interface

logger = logging.getLogger(__name__)


def sanitize_doc_id(doc_id):
    """Not strictly required, but remove slashes from Elastic Search ids"""
    return ':'.join(doc_id.split('/'))


class ESBase(object):
    """Shared code for Elastic Search storage models"""
    def __init__(self):
        self.es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)

    def safe_fetch(self, doc_type, es_id):
        """Attempt to retrieve a document from Elastic Search.
        :return: Found document, if it exists, otherwise None"""
        try:
            result = self.es.get(settings.ELASTIC_SEARCH_INDEX, doc_type,
                                 es_id)
            return result['_source']
        except ElasticHttpNotFoundError:
            return None

    def bulk_delete(self, *args, **kwarg):
        logger.warning("Elastic Search backend doesn't handle deletes")

    def delete(self, *args, **kwarg):
        logger.warning("Elastic Search backend doesn't handle deletes")


class ESDocuments(ESBase, interface.Documents):
    """Implementation of Elastic Search as regulations backend"""
    def get(self, doc_type, label, version):
        """Find the regulation label + version"""
        reg_node = self.safe_fetch('reg_tree', version + '/' + label)
        if reg_node is not None:
            del reg_node['regulation']
            del reg_node['version']
            del reg_node['label_string']
            del reg_node['id']
            return reg_node

    def _transform(self, reg, doc_type, version):
        """Add some meta data fields which are ES specific"""
        node = dict(reg)  # copy
        node['doc_type'] = doc_type
        node['version'] = version
        node['label_string'] = '-'.join(node['label'])
        node['regulation'] = node['label'][0]
        node['id'] = version + '/' + node['label_string']
        node['root'] = len(node['label']) == 1
        node['is_subpart'] = (
            'Subpart' in node['label'] or
            'Subjgrp' in node['label']
        )
        return node

    def bulk_insert(self, regs, doc_type, version):
        """Store all reg objects"""
        self.es.bulk_index(
            settings.ELASTIC_SEARCH_INDEX, 'reg_tree',
            [self._transform(r, doc_type, version) for r in regs],
        )

    def listing(self, doc_type, label=None):
        """List regulation version-label pairs that match this label (or are
        root, if label is None)"""
        if label is None:
            query = {'match': {'root': True, 'doc_type': doc_type}}
        else:
            query = {'match': {'label_string': label, 'doc_type': doc_type}}
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
        doc_id = sanitize_doc_id(layer.pop('doc_id'))
        return {'id': ':'.join([layer_name, doc_type, doc_id]), 'layer': layer}

    def bulk_insert(self, layers, layer_name, doc_type):
        """Store all layer objects."""
        self.es.bulk_index(
            settings.ELASTIC_SEARCH_INDEX, 'layer',
            [self._transform(l, layer_name, doc_type) for l in layers])

    def get(self, name, doc_type, doc_id):
        """Find the layer that matches these parameters"""
        reference = ':'.join([name, doc_type, sanitize_doc_id(doc_id)])
        layer = self.safe_fetch('layer', reference)
        if layer is not None:
            return layer['layer']


class ESNotices(ESBase, interface.Notices):
    """Implementation of Elastic Search as notice backend"""
    def insert(self, doc_number, notice):
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
        return '/'.join([label, old, new])

    def insert(self, label, old_version, new_version, diff):
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
