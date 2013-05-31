from core.db import *
from flasktest import FlaskTest
from mock import patch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

class ESRegulationsTest(FlaskTest):

    @patch('core.db.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esr = ESRegulations()

        self.assertEqual(None, esr.get('lablab', 'verver'))
        self.assertEqual('reg_tree', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/lablab', es.return_value.get.call_args[0][2])

    @patch('core.db.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = { '_source': {
            'first': 0, 'version': 'remove', 'id': 'also'
        }}
        esr = ESRegulations()

        self.assertEqual({"first": 0}, esr.get('lablab', 'verver'))
        self.assertEqual('reg_tree', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/lablab', es.return_value.get.call_args[0][2])

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
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esl = ESLayers()

        self.assertEqual(None, esl.get('namnam', 'lablab', 'verver'))
        self.assertEqual('layer', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/namnam/lablab', 
            es.return_value.get.call_args[0][2])

    @patch('core.db.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = { '_source': { 'layer': {
            'some': 'body'
        }}}
        esl = ESLayers()

        self.assertEqual({"some": 'body'}, 
                esl.get('namnam', 'lablab', 'verver'))
        self.assertEqual('layer', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/namnam/lablab', 
            es.return_value.get.call_args[0][2])

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
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esn = ESNotices()

        self.assertEqual(None, esn.get('docdoc'))
        self.assertEqual('notice', es.return_value.get.call_args[0][1])
        self.assertEqual('docdoc', es.return_value.get.call_args[0][2])

    @patch('core.db.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = { '_source': { 
            'some': 'body'
        }}
        esn = ESNotices()

        self.assertEqual({"some": 'body'}, esn.get('docdoc'))
        self.assertEqual('notice', es.return_value.get.call_args[0][1])
        self.assertEqual('docdoc', es.return_value.get.call_args[0][2])
 
    @patch('core.db.ElasticSearch')
    def test_put(self, es):
        esn = ESNotices()
        esn.put('docdoc', {"some": "structure"})
        self.assertTrue(es.return_value.index.called)
        args, kwargs = es.return_value.index.call_args
        self.assertEqual(3, len(args))
        self.assertEqual('notice', args[1])
        self.assertEqual({"some": "structure"}, args[2])
        self.assertTrue('id' in kwargs)
        self.assertEqual('docdoc', kwargs['id'])

    @patch('core.db.ElasticSearch')
    def test_all(self, es):
        es.return_value.search.return_value = { 'hits': { 'hits': [
            {'_id': 22, '_somethingelse': 5},
            {'_id': 9, '_somethingelse': 'blue'},
        ]}}
        esn = ESNotices()

        self.assertEqual([22, 9], esn.all())
        self.assertEqual('notice',
            es.return_value.search.call_args[1]['doc_type'])
 
