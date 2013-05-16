from core import app
from core.handlers.search import *
from flasktest import FlaskTest
from mock import patch

class HandlersSearchTest(FlaskTest):

    def test_search_missing_q(self):
        response = self.client.get('/search?non_q=test')
        self.assertEqual(400, response.status_code)
    
    @patch('core.handlers.search.ElasticSearch')
    def test_search_success(self, es):
        es.return_value.search.return_value = {'hits': {'hits': []}}
        response = self.client.get('/search?q=test')
        self.assertEqual(200, response.status_code)
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.search.called)
