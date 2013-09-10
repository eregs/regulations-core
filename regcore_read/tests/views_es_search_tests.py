from django.test import TestCase
from django.test.client import Client
from mock import patch

from regcore_read.views.es_search import *


class ViewsESSearchTest(TestCase):
    urls = 'regcore_read.tests.urls'

    def test_search_missing_q(self):
        response = Client().get('/es_search?non_q=test')
        self.assertEqual(400, response.status_code)

    @patch('regcore_read.views.es_search.ElasticSearch')
    def test_search_success(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [],
                                                        'total': 0}}
        response = Client().get('/es_search?q=test')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)

    @patch('regcore_read.views.es_search.ElasticSearch')
    def test_search_version(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [],
                                                        'total': 0}}
        response = Client().get('/es_search?q=test&version=12345678')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)
        self.assertTrue('12345678' in str(es.return_value.search.call_args))

    @patch('regcore_read.views.es_search.ElasticSearch')
    def test_search_version_regulation(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [],
                                                        'total': 0}}
        response = Client().get('/es_search?q=test&version=678&regulation=123')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)
        self.assertTrue('678' in str(es.return_value.search.call_args))
        self.assertTrue('123' in str(es.return_value.search.call_args))

    @patch('regcore_read.views.es_search.ElasticSearch')
    def test_search_paging(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [],
                                                        'total': 0}}
        response = Client().get('/es_search?q=test&page=5')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)
        query = es.return_value.search.call_args[0][0]
        self.assertEqual(50, query['size'])
        self.assertEqual(250, query['from'])

    @patch('regcore_read.views.es_search.db')
    def test_transform_results(self, db):
        # combine keyterms and terms into a single layer
        db.Layers.return_value.get.return_value = {
            '2': [{'key_term': 'k2'}], '3': [{'key_term': 'k3'}],
            '6': [{'key_term': 'k6'}], '7': [{'key_term': 'k7'}],
            'referenced': {
                'lab1': {'reference': '1', 'term': 'd1'},
                'lab2': {'reference': '3', 'term': 'd3'},
                'lab3': {'reference': '5', 'term': 'd5'},
                'lab4': {'reference': '7', 'term': 'd7'}
            }
        }
        results = transform_results([
            {'regulation': 'r', 'version': 'v', 'label_string': '0'},
            {'regulation': 'rr', 'version': 'v', 'label_string': '1'},
            {'regulation': 'r', 'version': 'vv', 'label_string': '2'},
            {'regulation': 'r', 'version': 'v', 'label_string': '3'},
            {'regulation': 'rr', 'version': 'vv', 'label_string': '4',
             'title': 't4'},
            {'regulation': 'r', 'version': 'vv', 'label_string': '5',
             'title': 't5'},
            {'regulation': 'rr', 'version': 'v', 'label_string': '6',
             'title': 't6'},
            {'regulation': 'r', 'version': 'v', 'label_string': '7',
             'title': 't7'}])

        self.assertFalse('title' in results[0])
        self.assertEqual('d1', results[1]['title'])
        self.assertEqual('k2', results[2]['title'])
        self.assertEqual('k3', results[3]['title'])
        self.assertEqual('t4', results[4]['title'])
        self.assertEqual('t5', results[5]['title'])
        self.assertEqual('t6', results[6]['title'])
        self.assertEqual('t7', results[7]['title'])
