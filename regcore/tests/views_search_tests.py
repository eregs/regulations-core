from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore.views.search import *


class ViewsSearchTest(TestCase):

    def test_search_missing_q(self):
        response = Client().get('/search?non_q=test')
        self.assertEqual(400, response.status_code)

    @patch('regcore.views.search.ElasticSearch')
    def test_search_success(self, es):
        es.return_value.search.return_value = {'hits': {'hits': []}}
        response = Client().get('/search?q=test')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)
