import json

from flasktest import FlaskTest
from mock import patch

from core import app
from core.handlers.diff import *


class HandlersDiffTest(FlaskTest):

    def setUp(self):
        FlaskTest.setUp(self)
        app.register_blueprint(blueprint)

    def test_add_not_json(self):
        url = '/diff/lablab/oldold/newnew'

        response = self.client.put(url, data = json.dumps({'some': 'struct'}))
        self.assertEqual(400, response.status_code)

        response = self.client.put(url, content_type='application/json',
            data = '{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_post(self):
        url = '/diff/lablab/oldold/newnew'

        response = self.client.post(url, content_type='application/json',
            data = json.dumps({'some': 'struct'}))
        self.assertEqual(405, response.status_code)

    @patch('core.handlers.diff.db')
    def test_add_label_success(self, db):
        url = '/diff/lablab/oldold/newnew'

        response = self.client.put(url, content_type='application/json',
            data = json.dumps({'some': 'struct'}))
        self.assertTrue(db.Diffs.return_value.put.called)
        args = db.Diffs.return_value.put.call_args[0]
        self.assertEqual(('lablab', 'oldold', 'newnew', {'some': 'struct'}),
            args)

    @patch('core.handlers.diff.db')
    def test_get_none(self, db):
        db.Diffs.return_value.get.return_value = None
        response = self.client.get('/diff/lablab/oldold/newnew')
        self.assertEqual(404, response.status_code)

    @patch('core.handlers.diff.db')
    def test_get_results(self, db):
        db.Diffs.return_value.get.return_value = {'example': 'response'}
        response = self.client.get('/diff/lablab/oldold/newnew')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'}, json.loads(response.data))
