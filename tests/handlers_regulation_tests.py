from core import app
from core.handlers.regulation import *
from flasktest import FlaskTest
import json
from mock import patch

class HandlersRegulationTest(FlaskTest):

    def test_add_not_json(self):
        url ='/regulation/lablab/verver'

        response = self.client.put(url, data = json.dumps(
            {'text': '', 'child': [], 'label': {'text': '', 'parts': []}}))
        self.assertEqual(400, response.status_code)

        response = self.client.put(url, content_type='application/json',
            data = '{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_invalid_json(self):
        url ='/regulation/lablab/verver'

        response = self.client.put(url, content_type='application/json',
            data = json.dumps({'incorrect': 'schema'}))
        self.assertEqual(400, response.status_code)

        message = {'text': '', 'label': {'text': '', 'parts': []}}
        response = self.client.put(url, content_type='application/json',
            data = json.dumps(message))
        self.assertEqual(400, response.status_code)

    def test_add_label_mismatch(self):
        url ='/regulation/lablab/verver'

        message = {'text': '', 'children': [], 
            'label': {'text': 'notlablba', 'parts': ['notlablab']}}
        response = self.client.put(url, content_type='application/json',
            data = json.dumps(message))
        self.assertEqual(400, response.status_code)

    def test_add_post(self):
        url ='/regulation/lablab/verver'

        message = {'text': '', 'children': [], 
            'label': {'text': 'lablba', 'parts': ['notlablab']}}
        response = self.client.post(url, content_type='application/json',
            data = json.dumps(message))
        self.assertEqual(405, response.status_code)

    @patch('core.handlers.regulation.ElasticSearch')
    def test_add_label_success(self, es):
        url = '/regulation/p/verver'

        message = {
            'text': 'parent text',
            'label': {'text': 'p', 'parts': ['p']},
            'children': [{
                'text': 'child1',
                'label': {'text': 'p-c1', 'parts': ['p', 'c1']},
                'children': []
            }, {
                'text': 'child2',
                'label': {'text': 'p-c2', 'parts': ['p', 'c2'], 
                    'title': 'My Title'},
                'children': []
            }]
        }
        response = self.client.put(url, content_type='application/json',
            data = json.dumps(message))
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.bulk_index.called)
        bulk_index_args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(bulk_index_args[2]))

    @patch('core.handlers.regulation.db')
    def test_get_good(self, db):
        url = '/regulation/lab/ver'
        db.Regulations.return_value.get.return_value = {"some": "thing"}
        response = self.client.get(url)
        self.assertTrue(db.Regulations.return_value.get.called)
        args = db.Regulations.return_value.get.call_args[0]
        self.assertTrue('lab' in args)
        self.assertTrue('ver' in args)
        self.assertEqual(200, response.status_code)
        self.assertEqual({'some': 'thing'}, json.loads(response.data))

    @patch('core.handlers.regulation.db')
    def test_get_404(self, db):
        url = '/regulation/lab/ver'
        db.Regulations.return_value.get.return_value = None
        response = self.client.get(url)
        self.assertTrue(db.Regulations.return_value.get.called)
        args = db.Regulations.return_value.get.call_args[0]
        self.assertTrue('lab' in args)
        self.assertTrue('ver' in args)
        self.assertEqual(404, response.status_code)
