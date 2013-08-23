from django.conf import settings
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError


class ESRegulations(object):
    """Implementation of Elastic Search as regulations backend"""
    def __init__(self):
        self.es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)

    def get(self, label, version):
        """Find the regulation label + version"""
        try:
            result = self.es.get(settings.ELASTIC_SEARCH_INDEX, 'reg_tree',
                                 version + '/' + label)

            reg_node = result['_source']
            del reg_node['version']
            del reg_node['label_string']
            del reg_node['id']
            return reg_node
        except ElasticHttpNotFoundError:
            return None

    def bulk_put(self, regs):
        """Store all reg objects"""
        self.es.bulk_index(settings.ELASTIC_SEARCH_INDEX, 'reg_tree', regs)

    def listing(self, label):
        """List regulation version that match this label"""
        query = {'match': {'label_string': label}}
        query = {'fields': ['version'], 'query': query}
        result = self.es.search(query, index=settings.ELASTIC_SEARCH_INDEX,
                                doc_type='reg_tree', size=100)
        return [res['fields']['version'] for res in result['hits']['hits']]


class ESLayers(object):
    """Implementation of Elastic Search as layers backend"""
    def __init__(self):
        self.es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)

    def bulk_put(self, layers):
        """Store all layer objects"""
        self.es.bulk_index(settings.ELASTIC_SEARCH_INDEX, 'layer', layers)

    def get(self, name, label, version):
        """Find the label that matches these parameters"""
        try:
            result = self.es.get(settings.ELASTIC_SEARCH_INDEX, 'layer',
                                 version + '/' + name + '/' + label)

            return result['_source']['layer']
        except ElasticHttpNotFoundError:
            return None


class ESNotices(object):
    """Implementation of Elastic Search as notice backend"""
    def __init__(self):
        self.es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)

    def put(self, doc_number, notice):
        """Store a single notice"""
        self.es.index(settings.ELASTIC_SEARCH_INDEX, 'notice', notice,
                      id=doc_number)

    def get(self, doc_number):
        """Find the associated notice"""
        try:
            result = self.es.get(settings.ELASTIC_SEARCH_INDEX, 'notice',
                                 doc_number)

            return result['_source']
        except ElasticHttpNotFoundError:
            return None

    def listing(self, part=None):
        """All notices or filtered by cfr_part"""
        if part:
            query = {'match': {'cfr_part': part}}
        else:
            query = {'match_all': {}}
        query = {'fields': ['effective_on', 'fr_url', 'publication_date'],
                 'query': query}
        result = self.es.search(query, index=settings.ELASTIC_SEARCH_INDEX,
                                doc_type='notice', size=100)
        notices = []
        results = self.es.search(query, doc_type='notice', size=100,
                                 index=settings.ELASTIC_SEARCH_INDEX)
        for notice in results['hits']['hits']:
            notice['fields']['document_number'] = notice['_id']
            notices.append(notice['fields'])
        return notices


class ESDiffs(object):
    """Implementation of Elastic Search as diff backend"""
    def __init__(self):
        self.es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)

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
        try:
            result = self.es.get(settings.ELASTIC_SEARCH_INDEX, 'diff',
                                 self.to_id(label, old_version, new_version))
            return result['_source']['diff']
        except ElasticHttpNotFoundError:
            return None
