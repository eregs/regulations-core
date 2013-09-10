import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_write.views.regulation import *


class ViewsRegulationTest(TestCase):

    def test_add_not_json(self):
        url = '/regulation/lablab/verver'

        response = Client().put(url, data=json.dumps(
            {'text': '', 'child': [], 'label': []}))
        self.assertEqual(400, response.status_code)

        response = Client().put(url, content_type='application/json',
                                data='{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_invalid_json(self):
        url = '/regulation/lablab/verver'

        response = Client().put(url, content_type='application/json',
                                data=json.dumps({'incorrect': 'schema'}))
        self.assertEqual(400, response.status_code)

        message = {'text': '', 'label': []}
        response = Client().put(url, content_type='application/json',
                                data=json.dumps(message))
        self.assertEqual(400, response.status_code)

    def test_add_label_mismatch(self):
        url = '/regulation/lablab/verver'

        message = {'text': '', 'children': [],
                   'label': ['notlablab']}
        response = Client().put(url, content_type='application/json',
                                data=json.dumps(message))
        self.assertEqual(400, response.status_code)

    @patch('regcore_write.views.regulation.db')
    def test_add_label_success(self, db):
        url = '/regulation/p/verver'

        message = {
            'text': 'parent text',
            'label': ['p'],
            'children': [{
                'text': 'child1',
                'label': ['p', 'c1'],
                'children': []
            }, {
                'text': 'child2',
                'label': ['p', 'c2'],
                'title': 'My Title',
                'children': []
            }]
        }

        response = Client().put(url, content_type='application/json',
                                data=json.dumps(message))
        self.assertTrue(db.Regulations.return_value.bulk_put.called)
        bulk_put_args = db.Regulations.return_value.bulk_put.call_args[0]
        self.assertEqual(3, len(bulk_put_args[0]))
        found = [False, False, False]
        for arg in bulk_put_args[0]:
            if arg['label'] == ['p']:
                found[0] = True
            if arg['label'] == ['p', 'c1']:
                found[1] = True
            if arg['label'] == ['p', 'c2']:
                found[2] = True
        self.assertEqual(found, [True, True, True])

        db.Regulations.return_value.bulk_put.reset_mock()
        response = Client().post(url, content_type='application/json',
                                 data=json.dumps(message))
        self.assertTrue(db.Regulations.return_value.bulk_put.called)
        bulk_put_args = db.Regulations.return_value.bulk_put.call_args[0]
        self.assertEqual(3, len(bulk_put_args[0]))

    @patch('regcore_write.views.regulation.db')
    def test_add_empty_children(self, db):
        url = '/regulation/p/verver'

        message = {
            'text': 'parent text',
            'label': ['p'],
            'children': []
        }
        response = Client().put(url, content_type='application/json',
                                data=json.dumps(message))
        self.assertTrue(db.Regulations.return_value.bulk_put.called)
        bulk_put_args = db.Regulations.return_value.bulk_put.call_args[0]
        self.assertEqual(1, len(bulk_put_args[0]))
