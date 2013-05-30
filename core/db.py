from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
import settings

class Regulations(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return ESRegulations()

    def get(self, label, version):
        """Documentation method. Returns a regulation node or None"""

    def bulk_put(self, regs):
        """Documentation method. Add many entries, each with an id field"""

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
            del reg_node['id']
            return reg_node
        except ElasticHttpNotFoundError:
            return None

    def bulk_put(self, regs):
        """Store all reg objects"""
        self.es.bulk_index(settings.ELASTIC_SEARCH_INDEX, 'reg_tree', regs)

class Layers(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return ESLayers()

    def bulk_put(self, layers):
        """Documentation method. Add many entries, each with an id field"""

    def get(self, name, label, version):
        """Doc method. Return a single layer (no meta data) or None"""

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

class Notices(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return ESNotices()

    def put(self, doc_number, notice):
        """Documentation method. doc_number:String, notice:Dict"""

    def get(self, doc_number):
        """Documentation method. Return matching notice or None"""

    def all(self):
        """Documentation method. Return all known notice ids"""

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

    def all(self):
        """Return all notice ids"""
        query = {'fields': ['id'], 'query': {'match_all' : {}}}
        result = self.es.search(query, index=settings.ELASTIC_SEARCH_INDEX,
                doc_type='notice', size=100)
        return [res['_id'] for res in result['hits']['hits']]
