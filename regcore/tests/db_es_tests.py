from contextlib import contextmanager
from unittest import TestCase

from mock import patch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from regcore.db.es import (
    ESDiffs, ESLayers, ESNotices, ESPreambles, ESRegulations)


class ESBase(object):
    """Mixin methods for boiler plate around mocking out Elastic Search. Each
    method sets the passed arguments as self.call_args"""
    @contextmanager
    def expect_get(self, doc_type, id, doc=None):
        """Expect an attempt to find a single document
           :param doc: document to return or None to test no document"""
        with patch('regcore.db.es.ElasticSearch') as es:
            if doc is None:
                es.return_value.get.side_effect = ElasticHttpNotFoundError
            else:
                es.return_value.get.return_value = {'_source': doc}
            yield
            self.call_args = es.return_value.get.call_args
        self.assertEqual((doc_type, id), self.call_args[0][1:])

    @contextmanager
    def expect_put(self, doc_type, id):
        """Expect a document to be written. Set the arguments passed to
        self.call_args"""
        with patch('regcore.db.es.ElasticSearch') as es:
            yield
            self.call_args = es.return_value.index.call_args
            self.assertEqual(doc_type, self.call_args[0][1])
            self.assertEqual(id, self.call_args[1].get('id'))

    @contextmanager
    def expect_bulk_put(self, doc_type, num_docs):
        """Expect multiple documents to be written.."""
        with patch('regcore.db.es.ElasticSearch') as es:
            yield
            self.call_args = es.return_value.bulk_index.call_args
            self.assertEqual(doc_type, self.call_args[0][1])
            self.assertEqual(num_docs, len(self.call_args[0][2]))

    @contextmanager
    def expect_search(self, doc_type, query, results):
        """Expect a search to be performed and respond with these results"""
        with patch('regcore.db.es.ElasticSearch') as es:
            es.return_value.search.return_value = {'hits': {'hits': results}}
            yield
            self.call_args = es.return_value.search.call_args
            self.assertEqual(self.call_args[1]['doc_type'], doc_type)
            self.assertEqual(query, self.call_args[0][0]['query'])


class ESRegulationsTest(TestCase, ESBase):
    def test_get_404(self):
        with self.expect_get('reg_tree', 'verver/lablab'):
            self.assertIsNone(ESRegulations().get('lablab', 'verver'))

    def test_get_success(self):
        return_value = {'first': 0, 'version': 'remove', 'id': 'also',
                        'label_string': 'a', 'regulation': '100'}
        with self.expect_get('reg_tree', 'verver/lablab', return_value):
            self.assertEqual(ESRegulations().get('lablab', 'verver'),
                             {"first": 0})

    def test_bulk_put(self):
        n2 = {'text': 'some text', 'label': ['111', '2'], 'children': []}
        n3 = {'text': 'other', 'label': ['111', '3'], 'children': []}
        # Use a copy of the children
        root = {'text': 'root', 'label': ['111'], 'children': [dict(n2),
                                                               dict(n3)]}
        nodes = [root, n2, n3]

        with self.expect_bulk_put('reg_tree', 3):
            ESRegulations().bulk_put(nodes, 'verver', '111')

        root.update({'version': 'verver', 'regulation': '111',
                     'label_string': '111', 'id': 'verver/111', 'root': True})
        n2.update({'version': 'verver', 'regulation': '111',
                   'label_string': '111-2', 'id': 'verver/111-2',
                   'root': False})
        n3.update({'version': 'verver', 'regulation': '111',
                   'label_string': '111-3', 'id': 'verver/111-3',
                   'root': False})
        self.assertEqual(nodes, self.call_args[0][2])

    def test_listing(self):
        query = {'match': {'label_string': 'lll'}}
        results = [{'fields': {'version': 'ver1', 'label_string': 'lll'}},
                   {'fields': {'version': 'aaa', 'label_string': 'lll'}},
                   {'fields': {'version': '333', 'label_string': 'lll'}},
                   {'fields': {'version': 'four', 'label_string': 'lll'}}]
        with self.expect_search('reg_tree', query, results):
            entries = ESRegulations().listing('lll')

        self.assertEqual([('333', 'lll'), ('aaa', 'lll'), ('four', 'lll'),
                          ('ver1', 'lll')], entries)

        query = {'match': {'root': True}}
        with self.expect_search('reg_tree', query, results):
            ESRegulations().listing()


class ESLayersTest(TestCase, ESBase):
    def test_get_404(self):
        with self.expect_get('layer', 'verver/namnam/lablab'):
            self.assertIsNone(ESLayers().get('namnam', 'lablab', 'verver'))

    def test_get_success(self):
        return_value = {'layer': {'some': 'body'}}
        with self.expect_get('layer', 'verver/namnam/lablab', return_value):
            self.assertEqual(ESLayers().get('namnam', 'lablab', 'verver'),
                             {"some": "body"})

    def test_bulk_put(self):
        layers = [{'111-22': [], '111-22-a': [], 'label': '111-22'},
                  {'111-23': [], 'label': '111-23'}]
        with self.expect_bulk_put('layer', 2):
            ESLayers().bulk_put(layers, 'verver', 'name', '111')

        del layers[0]['label']
        del layers[1]['label']
        transformed = [
            {'id': 'verver/name/111-22', 'version': 'verver',
             'name': 'name', 'label': '111-22', 'layer': layers[0]},
            {'id': 'verver/name/111-23', 'version': 'verver',
             'name': 'name', 'label': '111-23', 'layer': layers[1]}]
        self.assertEqual(transformed, self.call_args[0][2])


class ESNoticesTest(TestCase, ESBase):
    def test_get_404(self):
        with self.expect_get('notice', 'docdoc'):
            self.assertIsNone(ESNotices().get('docdoc'))

    def test_get_success(self):
        with self.expect_get('notice', 'docdoc', {'some': 'body'}):
            self.assertEqual(ESNotices().get('docdoc'),
                             {"some": 'body'})

    def test_put(self):
        with self.expect_put('notice', 'docdoc'):
            ESNotices().put('docdoc', {"some": "structure"})
        self.assertEqual(self.call_args[0][2], {"some": "structure"})

    def test_listing(self):
        query = {'match_all': {}}
        results = [{'_id': 22, '_somethingelse': 5, 'fields': {
                        'effective_on': '2005-05-05'}},
                   {'_id': 9, '_somethingelse': 'blue', 'fields': {}}]
        with self.expect_search('notice', query, results):
            entries = ESNotices().listing()

        self.assertEqual([{'document_number': 22,
                           'effective_on': '2005-05-05'},
                          {'document_number': 9}], entries)

        query = {'match': {'cfr_parts': '876'}}
        with self.expect_search('notice', query, results):
            ESNotices().listing('876')


class ESDiffTest(TestCase, ESBase):
    def test_get_404(self):
        with self.expect_get('diff', 'lablab/oldold/newnew'):
            self.assertIsNone(ESDiffs().get('lablab', 'oldold', 'newnew'))

    def test_get_success(self):
        return_value = {'label': 'lablab',
                        'old_version': 'oldold',
                        'new_version': 'newnew',
                        'diff': {'some': 'body'}}
        with self.expect_get('diff', 'lablab/oldold/newnew', return_value):
            self.assertEqual(ESDiffs().get('lablab', 'oldold', 'newnew'),
                             {"some": 'body'})

    def test_put(self):
        with self.expect_put('diff', 'lablab/oldold/newnew'):
            ESDiffs().put('lablab', 'oldold', 'newnew', {"some": "structure"})
        self.assertEqual(self.call_args[0][2],
                         {'label': 'lablab',
                          'old_version': 'oldold',
                          'new_version': 'newnew',
                          'diff': {'some': 'structure'}})


class ESPreamblesTest(TestCase, ESBase):
    def test_get_404(self):
        with self.expect_get('preamble', 'docdoc'):
            self.assertIsNone(ESPreambles().get('docdoc'))

    def test_get_success(self):
        with self.expect_get('preamble', 'docdoc', {'arbitrary': True}):
            self.assertEqual(ESPreambles().get('docdoc'), {'arbitrary': True})

    def test_put(self):
        with self.expect_put('preamble', 'docdoc'):
            ESPreambles().put('docdoc', {"some": "structure"})
        self.assertEqual(self.call_args[0][2], {"some": "structure"})
