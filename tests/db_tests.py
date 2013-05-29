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

    @patch('core.db.ElasticSearch')
    def test_bulk_put(self, es):
        esr = ESRegulations()
        esr.bulk_put([1, 2, 3, 4])
        self.assertTrue(es.return_value.bulk_index.called)
        args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(args))
        self.assertEqual('reg_tree', args[1])
        self.assertEqual([1,2,3,4], args[2])

class ESLayersTest(FlaskTest):

    @patch('core.db.ElasticSearch')
    def test_bulk_put(self, es):
        esl = ESLayers()
        esl.bulk_put([1, 2, 3, 4])
        self.assertTrue(es.return_value.bulk_index.called)
        args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(args))
        self.assertEqual('layer', args[1])
        self.assertEqual([1,2,3,4], args[2])

class ESNoticesTest(FlaskTest):

    @patch('core.db.ElasticSearch')
    def test_bulk_put(self, es):
        esr = ESNotices()
        esr.put('docdoc', {"some": "structure"})
        self.assertTrue(es.return_value.index.called)
        args, kwargs = es.return_value.index.call_args
        self.assertEqual(3, len(args))
        self.assertEqual('notice', args[1])
        self.assertEqual({"some": "structure"}, args[2])
        self.assertTrue('id' in kwargs)
        self.assertEqual('docdoc', kwargs['id'])
