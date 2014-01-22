from unittest import TestCase

from mock import patch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from regcore.db.es import *


class ESRegulationsTest(TestCase):

    @patch('regcore.db.es.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esr = ESRegulations()

        self.assertEqual(None, esr.get('lablab', 'verver'))
        self.assertEqual('reg_tree', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/lablab', es.return_value.get.call_args[0][2])

    @patch('regcore.db.es.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = {'_source': {
            'first': 0, 'version': 'remove', 'id': 'also',
            'label_string': 'a', 'regulation': '100'
        }}
        esr = ESRegulations()

        self.assertEqual({"first": 0}, esr.get('lablab', 'verver'))
        self.assertEqual('reg_tree', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/lablab', es.return_value.get.call_args[0][2])

    @patch('regcore.db.es.ElasticSearch')
    def test_bulk_put(self, es):
        esr = ESRegulations()
        n2 = {'text': 'some text', 'label': ['111', '2'], 'children': []}
        n3 = {'text': 'other', 'label': ['111', '3'], 'children': []}
        # Use a copy of the children
        root = {'text': 'root', 'label': ['111'], 'children': [dict(n2),
                                                               dict(n3)]}
        nodes = [root, n2, n3]
        esr.bulk_put(nodes, 'verver', '111')
        self.assertTrue(es.return_value.bulk_index.called)
        args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(args))
        self.assertEqual('reg_tree', args[1])

        root['version'] = 'verver'
        root['regulation'] = '111'
        root['label_string'] = '111'
        root['id'] = 'verver/111'
        root['root'] = True
        n2['version'] = 'verver'
        n2['regulation'] = '111'
        n2['label_string'] = '111-2'
        n2['id'] = 'verver/111-2'
        n2['root'] = False
        n3['version'] = 'verver'
        n3['label_string'] = '111-3'
        n3['regulation'] = '111'
        n3['id'] = 'verver/111-3'
        n3['root'] = False

        self.assertEqual(nodes, args[2])

    @patch('regcore.db.es.ElasticSearch')
    def test_listing(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [
            {'fields': {'version': 'ver1', 'label_string': 'lll'}},
            {'fields': {'version': 'aaa', 'label_string': 'lll'}},
            {'fields': {'version': '333', 'label_string': 'lll'}},
            {'fields': {'version': 'four', 'label_string': 'lll'}},
        ]}}
        esr = ESRegulations()
        results = esr.listing('lll')
        self.assertFalse('root' in str(es.return_value.search.call_args[0][0]))
        self.assertTrue('ll' in str(es.return_value.search.call_args[0][0]))
        self.assertEqual([('333', 'lll'), ('aaa', 'lll'), ('four', 'lll'),
                          ('ver1', 'lll')], results)

        results = esr.listing()
        self.assertTrue('root' in str(es.return_value.search.call_args[0][0]))
        self.assertFalse('ll' in str(es.return_value.search.call_args[0][0]))


class ESLayersTest(TestCase):

    @patch('regcore.db.es.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esl = ESLayers()

        self.assertEqual(None, esl.get('namnam', 'lablab', 'verver'))
        self.assertEqual('layer', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/namnam/lablab',
                         es.return_value.get.call_args[0][2])

    @patch('regcore.db.es.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = {'_source': {'layer': {
            'some': 'body'
        }}}
        esl = ESLayers()

        self.assertEqual({"some": 'body'},
                         esl.get('namnam', 'lablab', 'verver'))
        self.assertEqual('layer', es.return_value.get.call_args[0][1])
        self.assertEqual('verver/namnam/lablab',
                         es.return_value.get.call_args[0][2])

    @patch('regcore.db.es.ElasticSearch')
    def test_bulk_put(self, es):
        esl = ESLayers()
        layers = [
            {'111-22': [], '111-22-a': [], 'label': '111-22'},
            {'111-23': [], 'label': '111-23'}]
        esl.bulk_put(layers, 'verver', 'name', '111')
        self.assertTrue(es.return_value.bulk_index.called)
        args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(args))
        self.assertEqual('layer', args[1])

        del layers[0]['label']
        del layers[1]['label']
        transformed = [
            {'id': 'verver/name/111-22', 'version': 'verver',
             'name': 'name', 'label': '111-22', 'layer': layers[0]},
            {'id': 'verver/name/111-23', 'version': 'verver',
             'name': 'name', 'label': '111-23', 'layer': layers[1]}]

        self.assertEqual(transformed, args[2])


class ESNoticesTest(TestCase):

    @patch('regcore.db.es.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        esn = ESNotices()

        self.assertEqual(None, esn.get('docdoc'))
        self.assertEqual('notice', es.return_value.get.call_args[0][1])
        self.assertEqual('docdoc', es.return_value.get.call_args[0][2])

    @patch('regcore.db.es.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = {'_source': {
            'some': 'body'
        }}
        esn = ESNotices()

        self.assertEqual({"some": 'body'}, esn.get('docdoc'))
        self.assertEqual('notice', es.return_value.get.call_args[0][1])
        self.assertEqual('docdoc', es.return_value.get.call_args[0][2])

    @patch('regcore.db.es.ElasticSearch')
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

    @patch('regcore.db.es.ElasticSearch')
    def test_listing(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [
            {'_id': 22, '_somethingelse': 5, 'fields': {
                'effective_on': '2005-05-05'}},
            {'_id': 9, '_somethingelse': 'blue', 'fields': {}},
        ]}}
        esn = ESNotices()

        self.assertEqual([{'document_number': 22,
                           'effective_on': '2005-05-05'},
                          {'document_number': 9}], esn.listing())
        self.assertEqual('notice',
                         es.return_value.search.call_args[1]['doc_type'])

        self.assertEqual([{'document_number': 22,
                           'effective_on': '2005-05-05'},
                          {'document_number': 9}], esn.listing('876'))
        self.assertEqual('notice',
                         es.return_value.search.call_args[1]['doc_type'])
        self.assertTrue('876' in str(es.return_value.search.call_args[0][0]))


class ESDiffTest(TestCase):

    @patch('regcore.db.es.ElasticSearch')
    def test_get_404(self, es):
        es.return_value.get.side_effect = ElasticHttpNotFoundError
        eds = ESDiffs()

        self.assertEqual(None, eds.get('lablab', 'oldold', 'newnew'))
        self.assertEqual('diff', es.return_value.get.call_args[0][1])
        self.assertEqual('lablab/oldold/newnew',
                         es.return_value.get.call_args[0][2])

    @patch('regcore.db.es.ElasticSearch')
    def test_get_success(self, es):
        es.return_value.get.return_value = {'_source': {
            'label': 'lablab',
            'old_version': 'oldold',
            'new_version': 'newnew',
            'diff': {'some': 'body'}
        }}
        eds = ESDiffs()

        self.assertEqual({"some": 'body'},
                         eds.get('lablab', 'oldold', 'newnew'))
        self.assertEqual('diff', es.return_value.get.call_args[0][1])
        self.assertEqual('lablab/oldold/newnew',
                         es.return_value.get.call_args[0][2])

    @patch('regcore.db.es.ElasticSearch')
    def test_put(self, es):
        eds = ESDiffs()
        eds.put('lablab', 'oldold', 'newnew', {"some": "structure"})
        self.assertTrue(es.return_value.index.called)
        args, kwargs = es.return_value.index.call_args
        self.assertEqual(3, len(args))
        self.assertEqual('diff', args[1])
        self.assertEqual('lablab/oldold/newnew', kwargs['id'])
        self.assertEqual({
            'label': 'lablab',
            'old_version': 'oldold',
            'new_version': 'newnew',
            'diff': {'some': 'structure'}
        }, args[2])
