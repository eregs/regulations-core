from pyelasticsearch import ElasticSearch
import settings

class Regulations(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return ESRegulations()

    def get(self, label, version):
        """Documentation method. Returns a regulation node or None"""

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
