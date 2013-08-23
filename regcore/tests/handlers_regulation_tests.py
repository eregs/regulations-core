import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore.views.regulation import *


class HandlersRegulationTest(TestCase):
    
    def test_add_not_json(self):
        url ='/regulation/lablab/verver'

        response = Client().put(url, data = json.dumps(
            {'text': '', 'child': [], 'label': []}))
        self.assertEqual(400, response.status_code)

        response = Client().put(url, content_type='application/json',
            data = '{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_invalid_json(self):
        url ='/regulation/lablab/verver'

        response = Client().put(url, content_type='application/json',
            data = json.dumps({'incorrect': 'schema'}))
        self.assertEqual(400, response.status_code)

        message = {'text': '', 'label': []}
        response = Client().put(url, content_type='application/json',
            data = json.dumps(message))
        self.assertEqual(400, response.status_code)

    def test_add_label_mismatch(self):
        url ='/regulation/lablab/verver'

        message = {'text': '', 'children': [], 
            'label': ['notlablab']}
        response = Client().put(url, content_type='application/json',
            data = json.dumps(message))
        self.assertEqual(400, response.status_code)

    def test_add_post(self):
        url ='/regulation/lablab/verver'

        message = {'text': '', 'children': [], 
            'label': ['notlablab']}
        response = Client().post(url, content_type='application/json',
            data = json.dumps(message))
        self.assertEqual(405, response.status_code)

    @patch('regcore.views.regulation.db')
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
            data = json.dumps(message))
        self.assertTrue(db.Regulations.return_value.bulk_put.called)
        bulk_put_args = db.Regulations.return_value.bulk_put.call_args[0]
        self.assertEqual(3, len(bulk_put_args[0]))
        found = [False, False, False]
        for arg in bulk_put_args[0]:
            self.assertEqual(arg['version'], 'verver')
            if arg['label_string'] == 'p' and arg['id'] == 'verver/p':
                found[0] = True
            if arg['label_string'] == 'p-c1' and arg['id'] == 'verver/p-c1':
                found[1] = True
            if arg['label_string'] == 'p-c2' and arg['id'] == 'verver/p-c2':
                found[2] = True
        self.assertEqual(found, [True, True, True])

    @patch('regcore.views.regulation.db')
    def test_add_empty_children(self, db):
        url = '/regulation/p/verver'

        message = {
            'text': 'parent text',
            'label': ['p'],
            'children': []
        }
        response = Client().put(url, content_type='application/json',
            data = json.dumps(message))
        self.assertTrue(db.Regulations.return_value.bulk_put.called)
        bulk_put_args = db.Regulations.return_value.bulk_put.call_args[0]
        self.assertEqual(1, len(bulk_put_args[0]))

    @patch('regcore.views.regulation.db')
    def test_get_good(self, db):
        url = '/regulation/lab/ver'
        db.Regulations.return_value.get.return_value = {"some": "thing"}
        response = Client().get(url)
        self.assertTrue(db.Regulations.return_value.get.called)
        args = db.Regulations.return_value.get.call_args[0]
        self.assertTrue('lab' in args)
        self.assertTrue('ver' in args)
        self.assertEqual(200, response.status_code)
        self.assertEqual({'some': 'thing'}, json.loads(response.content))

    @patch('regcore.views.regulation.db')
    def test_get_404(self, db):
        url = '/regulation/lab/ver'
        db.Regulations.return_value.get.return_value = None
        response = Client().get(url)
        self.assertTrue(db.Regulations.return_value.get.called)
        args = db.Regulations.return_value.get.call_args[0]
        self.assertTrue('lab' in args)
        self.assertTrue('ver' in args)
        self.assertEqual(404, response.status_code)

    @patch('regcore.views.regulation.db')
    def test_listing(self, db):
        url = '/regulation/lablab'
        db.Notices.return_value.listing.return_value = [
            {'document_number': '10', 'effective_on': '2010-10-10'},
            {'document_number': '15', 'effective_on': '2010-10-10'},
            {'document_number': '12'},
            {'document_number': '20', 'effective_on': '2011-11-11'},
            {'document_number': '25', 'effective_on': '2011-11-11'}
        ]
        db.Regulations.return_value.listing.return_value = ['10', '15', '20']

        response = Client().get(url)
        self.assertEqual(200, response.status_code)
        found = [False, False, False]
        for ver in json.loads(response.content)['versions']:
            if ver['version'] == '10' and 'by_date' not in ver:
                found[0] = True
            if ver['version'] == '15' and ver['by_date'] == '2010-10-10':
                found[1] = True
            if ver['version'] == '20' and ver['by_date'] == '2011-11-11':
                found[2] = True
        self.assertEqual(found, [True, True, True])
