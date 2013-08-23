import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore.views.diff import *


class ViewsDiffTest(TestCase):

    def test_add_not_json(self):
        url = '/diff/lablab/oldold/newnew'

        response = Client().put(url, content_type='application/json',
                                   data='{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_post(self):
        url = '/diff/lablab/oldold/newnew'

        response = Client().post(url, content_type='application/json',
                                    data=json.dumps({'some': 'struct'}))
        self.assertEqual(405, response.status_code)

    @patch('regcore.views.diff.db')
    def test_add_label_success(self, db):
        url = '/diff/lablab/oldold/newnew'

        response = Client().put(url, content_type='application/json',
                                   data=json.dumps({'some': 'struct'}))
        self.assertTrue(db.Diffs.return_value.put.called)
        args = db.Diffs.return_value.put.call_args[0]
        self.assertEqual(('lablab', 'oldold', 'newnew', {'some': 'struct'}),
                         args)

    @patch('regcore.views.diff.db')
    def test_get_none(self, db):
        db.Diffs.return_value.get.return_value = None
        response = Client().get('/diff/lablab/oldold/newnew')
        self.assertEqual(404, response.status_code)

    @patch('regcore.views.diff.db')
    def test_get_results(self, db):
        db.Diffs.return_value.get.return_value = {'example': 'response'}
        response = Client().get('/diff/lablab/oldold/newnew')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content))
