import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_read.views.diff import *


class ViewsDiffTest(TestCase):

    @patch('regcore_read.views.diff.db')
    def test_get_none(self, db):
        db.Diffs.return_value.get.return_value = None
        response = Client().get('/diff/lablab/oldold/newnew')
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.diff.db')
    def test_get_results(self, db):
        db.Diffs.return_value.get.return_value = {'example': 'response'}
        response = Client().get('/diff/lablab/oldold/newnew')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content))
