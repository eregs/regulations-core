import json
from unittest import TestCase

from django.test.client import Client
from mock import patch


class ViewsDiffTest(TestCase):
    @patch('regcore_read.views.diff.storage')
    def test_get_none(self, storage):
        storage.for_diffs.get.return_value = None
        response = Client().get('/diff/lablab/oldold/newnew')
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.diff.storage')
    def test_get_empty(self, storage):
        storage.for_diffs.get.return_value = {}
        response = Client().get('/diff/lablab/oldold/newnew')
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.content.decode('utf-8')))

    @patch('regcore_read.views.diff.storage')
    def test_get_results(self, storage):
        storage.for_diffs.get.return_value = {'example': 'response'}
        response = Client().get('/diff/lablab/oldold/newnew')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content.decode('utf-8')))
