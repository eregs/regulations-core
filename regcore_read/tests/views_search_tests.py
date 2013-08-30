from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_read.views.search import *


class ViewsSearchTest(TestCase):

    def test_search_missing_q(self):
        response = Client().get('/search?non_q=test')
        self.assertEqual(400, response.status_code)

    @patch('regcore_read.views.search.ElasticSearch')
    def test_search_success(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [],
                                                        'total': 0}}
        response = Client().get('/search?q=test')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)

    @patch('regcore_read.views.search.ElasticSearch')
    def test_search_version(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [],
                                                        'total': 0}}
        response = Client().get('/search?q=test&version=12345678')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)
        self.assertTrue('12345678' in str(es.return_value.search.call_args))

    @patch('regcore_read.views.search.ElasticSearch')
    def test_search_paging(self, es):
        es.return_value.search.return_value = {'hits': {'hits': [],
                                                        'total': 0}}
        response = Client().get('/search?q=test&page=5')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)
        query = es.return_value.search.call_args[0][0]
        self.assertEqual(50, query['size'])
        self.assertEqual(250, query['from'])
