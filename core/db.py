from pyelasticsearch import ElasticSearch
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
        query = {'query': {'match': {'id': version + '/' + label }}}
        results = self.es.search(query, index=settings.ELASTIC_SEARCH_INDEX)

        if results['hits']['hits']:
            reg_node = results['hits']['hits'][0]['_source']
            del reg_node['version']
            del reg_node['id']
            return reg_node

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

class ESLayers(object):
    """Implementation of Elastic Search as layers backend"""
    def __init__(self):
        self.es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)

    def bulk_put(self, layers):
        """Store all layer objects"""
        self.es.bulk_index(settings.ELASTIC_SEARCH_INDEX, 'layer', regs)
