import json
from unittest import TestCase

from django.test.client import Client
from mock import patch


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

    @patch('regcore_write.views.document.storage')
    def test_add_label_success(self, storage):
        url = '/regulation/p/verver'

        message = {
            'text': 'parent text',
            'label': ['p'],
            'node_type': 'reg_text',
            'children': [{
                'text': 'child1',
                'label': ['p', 'c1'],
                'node_type': 'reg_text',
                'children': []
            }, {
                'text': 'child2',
                'label': ['p', 'c2'],
                'title': 'My Title',
                'node_type': 'reg_text',
                'children': []
            }]
        }

        Client().put(url, content_type='application/json',
                     data=json.dumps(message))
        self.assertTrue(storage.for_documents.bulk_insert.called)
        bulk_insert_args = storage.for_documents.bulk_insert.call_args[0]
        self.assertEqual(3, len(bulk_insert_args[0]))
        found = [False, False, False]
        for arg in bulk_insert_args[0]:
            if arg['label'] == ['p']:
                found[0] = True
            if arg['label'] == ['p', 'c1']:
                found[1] = True
            if arg['label'] == ['p', 'c2']:
                found[2] = True
        self.assertEqual(found, [True, True, True])

        storage.for_documents.bulk_insert.reset_mock()
        Client().post(url, content_type='application/json',
                      data=json.dumps(message))
        self.assertTrue(storage.for_documents.bulk_insert.called)
        bulk_insert_args = storage.for_documents.bulk_insert.call_args[0]
        self.assertEqual(3, len(bulk_insert_args[0]))

    @patch('regcore_write.views.document.storage')
    def test_add_empty_children(self, storage):
        url = '/regulation/p/verver'

        message = {
            'text': 'parent text',
            'label': ['p'],
            'children': []
        }
        Client().put(url, content_type='application/json',
                     data=json.dumps(message))
        self.assertTrue(storage.for_documents.bulk_insert.called)
        bulk_insert_args = storage.for_documents.bulk_insert.call_args[0]
        self.assertEqual(1, len(bulk_insert_args[0]))
