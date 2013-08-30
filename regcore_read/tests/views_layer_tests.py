import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_read.views.layer import *


class ViewsLayerTest(TestCase):

    @patch('regcore_read.views.layer.db')
    def test_get_none(self, db):
        url = '/layer/layname/lablab/verver'

        db.Layers.return_value.get.return_value = None
        response = Client().get(url)
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.layer.db')
    def test_get_results(self, db):
        db.Layers.return_value.get.return_value = {'example': 'response'}
        response = Client().get('/layer/nnn/lll/vvv')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content))

    @patch('regcore_read.views.layer.db')
    def test_get_results_empty_layer(self, db):
        db.Layers.return_value.get.return_value = {}
        response = Client().get('/layer/nnn/lll/vvv')
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.content))
