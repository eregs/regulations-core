from contextlib import contextmanager
from unittest import TestCase

from mock import patch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from regcore.db.es import ESDiffs, ESDocuments, ESLayers, ESNotices


class ESBase(object):
    """Mixin methods for boiler plate around mocking out Elastic Search. Each
    method yields the appropriate, mocked Elastic Search fn"""
    @contextmanager
    def expect_get(self, doc_type, ident, doc=None):
        """Expect an attempt to find a single document
           :param doc: document to return or None to test no document"""
        with patch('regcore.db.es.ElasticSearch') as es:
            if doc is None:
                es.return_value.get.side_effect = ElasticHttpNotFoundError
            else:
                es.return_value.get.return_value = {'_source': doc}
            yield es.return_value.get
            self.assertEqual((doc_type, ident),
                             es.return_value.get.call_args[0][1:])

    @contextmanager
    def expect_insert(self, doc_type, ident):
        """Expect a document to be written."""
        with patch('regcore.db.es.ElasticSearch') as es:
            yield es.return_value.index
            self.assertEqual(doc_type, es.return_value.index.call_args[0][1])
            self.assertEqual(ident,
                             es.return_value.index.call_args[1].get('id'))

    @contextmanager
    def expect_bulk_insert(self, doc_type, num_docs):
        """Expect multiple documents to be written.."""
        with patch('regcore.db.es.ElasticSearch') as es:
            yield es.return_value.bulk_index
            self.assertEqual(doc_type,
                             es.return_value.bulk_index.call_args[0][1])
            self.assertEqual(num_docs,
                             len(es.return_value.bulk_index.call_args[0][2]))

    @contextmanager
    def expect_search(self, doc_type, query, results):
        """Expect a search to be performed and respond with these results"""
        with patch('regcore.db.es.ElasticSearch') as es:
            es.return_value.search.return_value = {'hits': {'hits': results}}
            yield es.return_value.search
            self.assertEqual(es.return_value.search.call_args[1]['doc_type'],
                             doc_type)
            self.assertEqual(es.return_value.search.call_args[0][0]['query'],
                             query)


class ESDocumentsTest(TestCase, ESBase):
    def test_get_404(self):
        with self.expect_get('reg_tree', 'verver/lablab'):
            self.assertIsNone(ESDocuments().get('cfr', 'lablab', 'verver'))

    def test_get_success(self):
        return_value = {'first': 0, 'version': 'remove', 'id': 'also',
                        'label_string': 'a', 'regulation': '100'}
        with self.expect_get('reg_tree', 'verver/lablab', return_value):
            self.assertEqual(ESDocuments().get('cfr', 'lablab', 'verver'),
                             {"first": 0})

    def test_bulk_insert(self):
        n2 = {'text': 'some text', 'label': ['111', '2'], 'children': []}
        n3 = {'text': 'other', 'label': ['111', '3'], 'children': []}
        # Use a copy of the children
        root = {'text': 'root', 'label': ['111'], 'children': [dict(n2),
                                                               dict(n3)]}
        nodes = [root, n2, n3]

        with self.expect_bulk_insert('reg_tree', 3) as bulk_insert:
            ESDocuments().bulk_insert(nodes, 'cfr', 'verver')

        root.update({'version': 'verver', 'regulation': '111',
                     'label_string': '111', 'id': 'verver/111', 'root': True,
                     'is_subpart': False})
        n2.update({'version': 'verver', 'regulation': '111',
                   'label_string': '111-2', 'id': 'verver/111-2',
                   'root': False, 'is_subpart': False})
        n3.update({'version': 'verver', 'regulation': '111',
                   'label_string': '111-3', 'id': 'verver/111-3',
                   'root': False, 'is_subpart': False})
        bulk_data = [dict(root), dict(n2), dict(n3)]
        for node in bulk_data:
            node['doc_type'] = 'cfr'
        self.assertEqual(bulk_data, bulk_insert.call_args[0][2])

    def test_listing(self):
        query = {'match': {'label_string': 'lll', 'doc_type': 'cfr'}}
        results = [{'fields': {'version': 'ver1', 'label_string': 'lll'}},
                   {'fields': {'version': 'aaa', 'label_string': 'lll'}},
                   {'fields': {'version': '333', 'label_string': 'lll'}},
                   {'fields': {'version': 'four', 'label_string': 'lll'}}]
        with self.expect_search('reg_tree', query, results):
            entries = ESDocuments().listing('cfr', 'lll')

        self.assertEqual([('333', 'lll'), ('aaa', 'lll'), ('four', 'lll'),
                          ('ver1', 'lll')], entries)

        query = {'match': {'root': True, 'doc_type': 'cfr'}}
        with self.expect_search('reg_tree', query, results):
            ESDocuments().listing('cfr')


class ESLayersTest(TestCase, ESBase):
    def test_get_404(self):
        with self.expect_get('layer', 'namnam:cfr:verver:lablab'):
            self.assertIsNone(
                ESLayers().get('namnam', 'cfr', 'verver:lablab'))

    def test_get_success(self):
        with self.expect_get('layer', 'namnam:cfr:verver:lablab',
                             {'layer': {'some': 'body'}}):
            self.assertEqual(ESLayers().get('namnam', 'cfr', 'verver:lablab'),
                             {"some": "body"})

    def test_bulk_insert(self):
        layers = [{'111-22': [], '111-22-a': [], 'doc_id': 'verver:111-22'},
                  {'111-23': [], 'doc_id': 'verver:111-23'}]
        with self.expect_bulk_insert('layer', 2) as bulk_insert:
            ESLayers().bulk_insert(layers, 'name', 'cfr')

        del layers[0]['doc_id']
        del layers[1]['doc_id']
        transformed = [{'id': 'name:cfr:verver:111-22', 'layer': layers[0]},
                       {'id': 'name:cfr:verver:111-23', 'layer': layers[1]}]
        self.assertEqual(transformed, bulk_insert.call_args[0][2])


class ESNoticesTest(TestCase, ESBase):
    def test_get_404(self):
        with self.expect_get('notice', 'docdoc'):
            self.assertIsNone(ESNotices().get('docdoc'))

    def test_get_success(self):
        with self.expect_get('notice', 'docdoc', {'some': 'body'}):
            self.assertEqual(ESNotices().get('docdoc'),
                             {"some": 'body'})

    def test_insert(self):
        with self.expect_insert('notice', 'docdoc') as insert:
            ESNotices().insert('docdoc', {"some": "structure"})
        self.assertEqual(insert.call_args[0][2], {"some": "structure"})

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

    def test_insert(self):
        with self.expect_insert('diff', 'lablab/oldold/newnew') as insert:
            ESDiffs().insert('lablab', 'oldold', 'newnew',
                             {"some": "structure"})
        self.assertEqual(insert.call_args[0][2],
                         {'label': 'lablab',
                          'old_version': 'oldold',
                          'new_version': 'newnew',
                          'diff': {'some': 'structure'}})
