import json
from unittest import TestCase

from django.test.client import Client
from mock import patch


class ViewsLayerTest(TestCase):

    @patch('regcore_read.views.layer.storage')
    def test_get_none(self, storage):
        url = '/layer/layname/lablab/verver'

        storage.for_layers.get.return_value = None
        response = Client().get(url)
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.layer.storage')
    def test_get_results(self, storage):
        storage.for_layers.get.return_value = {'example': 'response'}
        response = Client().get('/layer/nnn/lll/vvv')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content.decode('utf-8')))

    @patch('regcore_read.views.layer.storage')
    def test_get_results_empty_layer(self, storage):
        storage.for_layers.get.return_value = {}
        response = Client().get('/layer/nnn/lll/vvv')
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.content.decode('utf-8')))
