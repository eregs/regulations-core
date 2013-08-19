from core.db.es import *
from flasktest import FlaskTest
from mock import patch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

class ESRegulationsTest(FlaskTest):

    @patch('core.db.es.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esr = ESRegulations()

        self.assertEqual(None, esr.get('lablab', 'verver'))
        self.assertEqual('reg_tree', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/lablab', es.return_value.get.call_args[0][2])

    @patch('core.db.es.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = { '_source': {
            'first': 0, 'version': 'remove', 'id': 'also', 'label_string': 'a'
        }}
        esr = ESRegulations()

        self.assertEqual({"first": 0}, esr.get('lablab', 'verver'))
        self.assertEqual('reg_tree', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/lablab', es.return_value.get.call_args[0][2])

    @patch('core.db.es.ElasticSearch')
    def test_bulk_put(self, es):
        esr = ESRegulations()
        esr.bulk_put([1, 2, 3, 4])
        self.assertTrue(es.return_value.bulk_index.called)
        args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(args))
        self.assertEqual('reg_tree', args[1])
        self.assertEqual([1,2,3,4], args[2])

    @patch('core.db.es.ElasticSearch')
    def test_listing(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [
            {'fields': {'version': 'ver1'}}, {'fields': {'version': 'aaa'}},
            {'fields': {'version': '333'}}, {'fields': {'version': 'four'}},
        ]}}
        esr = ESRegulations()
        results = esr.listing('lll')
        self.assertTrue('ll' in str(es.return_value.search.call_args[0][0]))
        self.assertEqual(['ver1', 'aaa', '333', 'four'], results)

class ESLayersTest(FlaskTest):

    @patch('core.db.es.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esl = ESLayers()

        self.assertEqual(None, esl.get('namnam', 'lablab', 'verver'))
        self.assertEqual('layer', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/namnam/lablab', 
            es.return_value.get.call_args[0][2])

    @patch('core.db.es.ElasticSearch')
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

    @patch('core.db.es.ElasticSearch')
    def test_bulk_put(self, es):
        esl = ESLayers()
        esl.bulk_put([1, 2, 3, 4])
        self.assertTrue(es.return_value.bulk_index.called)
        args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(args))
        self.assertEqual('layer', args[1])
        self.assertEqual([1,2,3,4], args[2])

class ESNoticesTest(FlaskTest):

    @patch('core.db.es.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esn = ESNotices()

        self.assertEqual(None, esn.get('docdoc'))
        self.assertEqual('notice', es.return_value.get.call_args[0][1])
        self.assertEqual('docdoc', es.return_value.get.call_args[0][2])

    @patch('core.db.es.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = { '_source': { 
            'some': 'body'
        }}
        esn = ESNotices()

        self.assertEqual({"some": 'body'}, esn.get('docdoc'))
        self.assertEqual('notice', es.return_value.get.call_args[0][1])
        self.assertEqual('docdoc', es.return_value.get.call_args[0][2])
 
    @patch('core.db.es.ElasticSearch')
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

    @patch('core.db.es.ElasticSearch')
    def test_listing(self, es):
        es.return_value.search.return_value = { 'hits': { 'hits': [
            {'_id': 22, '_somethingelse': 5, 'fields':{
                'effective_on': '2005-05-05'}},
            {'_id': 9, '_somethingelse': 'blue', 'fields': {}},
        ]}}
        esn = ESNotices()

        self.assertEqual([{'document_number': 22, 'effective_on': '2005-05-05'},
                          {'document_number': 9}], esn.listing())
        self.assertEqual('notice',
            es.return_value.search.call_args[1]['doc_type'])
 
        self.assertEqual([{'document_number': 22, 'effective_on': '2005-05-05'},
                          {'document_number': 9}], esn.listing('876'))
        self.assertEqual('notice',
            es.return_value.search.call_args[1]['doc_type'])
        self.assertTrue('876' in str(es.return_value.search.call_args[0][0]))
 
