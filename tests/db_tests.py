from core.db import *
from flasktest import FlaskTest
from mock import patch

class ESRegulationsTest(FlaskTest):

    @patch('core.db.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.search.return_value = {'hits': {'hits': []}}
        esr = ESRegulations()

        self.assertEqual(None, esr.get('lablab', 'verver'))
        self.assertEqual('verver/lablab',
                es.return_value.search.call_args[0][0]['query']['match']['id'])

    @patch('core.db.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [
            {"_source": {"first": 0, "version": "remove", "id": "also"}}, 
            {"_source": {"second": 1}}
        ]}}
        esr = ESRegulations()

        self.assertEqual({"first": 0}, esr.get('lablab', 'verver'))
        self.assertEqual('verver/lablab',
                es.return_value.search.call_args[0][0]['query']['match']['id'])
