import json

from django.test import TestCase
from mock import patch


class ViewsLayerTest(TestCase):

    @patch('regcore_read.views.layer.storage')
    def test_get_none(self, storage):
        url = '/layer/layname/cfr/verver/lablab'

        storage.for_layers.get.return_value = None
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.layer.storage')
    def test_get_results(self, storage):
        """Verify that a request to GET a specific layer hits the backend with
        appropriate version info"""
        storage.for_layers.get.return_value = {'example': 'response'}
        response = self.client.get('/layer/nnn/cfr/vvv/lll')
        self.assertEqual(200, response.status_code)
        self.assertEqual(storage.for_layers.get.call_args[0],
                         ('nnn', 'cfr', 'vvv/lll'))
        self.assertEqual({'example': 'response'},
                         json.loads(response.content.decode('utf-8')))

        response = self.client.get('/layer/nnn/preamble/lll')
        self.assertEqual(storage.for_layers.get.call_args[0],
                         ('nnn', 'preamble', 'lll'))
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content.decode('utf-8')))

    @patch('regcore_read.views.layer.storage')
    def test_get_results_empty_layer(self, storage):
        storage.for_layers.get.return_value = {}
        response = self.client.get('/layer/nnn/cfr/vvv/lll')
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.content.decode('utf-8')))
