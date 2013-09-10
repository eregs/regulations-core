import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_write.views.layer import *


class ViewsLayerTest(TestCase):

    def test_add_not_json(self):
        url = '/layer/layname/lablab/verver'

        response = Client().put(url, content_type='application/json',
                                data='{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_label_mismatch(self):
        url = '/layer/layname/lablab/verver'

        response = Client().put(url, content_type='application/json',
                                data=json.dumps({'nonlab': []}))
        self.assertEqual(400, response.status_code)

    @patch('regcore_write.views.layer.db')
    def test_add_success(self, db):
        url = '/layer/layname/lablab/verver'

        message = {
            'lablab': [1, 2],
            'lablab-b': [2, 3],
            'lablab-b-4': [3, 4],
        }
        db.Regulations.return_value.get.return_value = {
            'label': ['lablab'],
            'children': [{
                'label': ['lablab', 'b'],
                'children': [{
                    'label': ['lablab', 'b', '4'],
                    'children': []
                }]
            }]
        }
        response = Client().put(url, content_type='application/json',
                                data=json.dumps(message))
        self.assertTrue(db.Layers.return_value.bulk_put.called)
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        args = list(reversed(args))   # switch to outside in

        self.assertEqual(3, len(args))
        message['label'] = 'lablab'
        self.assertEqual(message, args[0])

        #   Sub layers have fewer elements
        del message['lablab']
        message['label'] = 'lablab-b'
        self.assertEqual(message, args[1])
        del message['lablab-b']
        message['label'] = 'lablab-b-4'
        self.assertEqual(message, args[2])

    @patch('regcore_write.views.layer.db')
    def test_add_skip_level(self, db):
        url = '/layer/layname/lablab/verver'

        message = {
            'lablab': [1, 2],
            'lablab-b-4': [3, 4],
        }
        db.Regulations.return_value.get.return_value = {
            'label': ['lablab'],
            'children': [{
                'label': ['lablab', 'b'],
                'children': [{
                    'label': ['lablab', 'b', '4'],
                    'children': []
                }]
            }]
        }
        response = Client().put(url, content_type='application/json',
                                data=json.dumps(message))
        self.assertTrue(db.Layers.return_value.bulk_put.called)
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        args = list(reversed(args))   # switch to outside in

        self.assertEqual(3, len(args))
        message['label'] = 'lablab'
        self.assertEqual(message, args[0])
        #   Sub layers have fewer elements
        del message['lablab']
        message['label'] = 'lablab-b'
        self.assertEqual(message, args[1])
        message['label'] = 'lablab-b-4'
        self.assertEqual(message, args[2])

    @patch('regcore_write.views.layer.db')
    def test_add_interp_children(self, db):
        url = '/layer/layname/99/verver'

        message = {'99-5-Interp': [1, 2], '99-5-a-Interp': [3, 4]}
        db.Regulations.return_value.get.return_value = {
            'label': ['99'],
            'children': [{
                'label': ['99', 'Interp'],
                'children': [{
                    'label': ['99', '5', 'Interp'],
                    'children': [{
                        'label': ['99', '5', 'a', 'Interp'],
                        'children': [],
                    }]
                }]
            }]
        }
        Client().put(url, content_type='application/json',
                     data=json.dumps(message))
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        self.assertEqual(4, len(args))
        args = list(reversed(args))   # switch to outside in
        self.assertTrue('99-5-Interp' in args[0])
        self.assertTrue('99-5-a-Interp' in args[0])
        self.assertTrue('99-5-Interp' in args[1])
        self.assertTrue('99-5-a-Interp' in args[1])
        self.assertTrue('99-5-Interp' in args[2])
        self.assertTrue('99-5-a-Interp' in args[2])
        self.assertFalse('99-5-Interp' in args[3])
        self.assertTrue('99-5-a-Interp' in args[3])

    @patch('regcore_write.views.layer.db')
    def test_add_subpart_children(self, db):
        url = '/layer/layname/99/verver'

        message = {'99-1': [1, 2], '99-1-a': [3, 4]}
        db.Regulations.return_value.get.return_value = {
            'label': ['99'],
            'children': [{
                'label': ['99', 'Subpart', 'A'],
                'children': [{
                    'label': ['99', '1'],
                    'children': [{
                        'label': ['99', '1', 'a'],
                        'children': []
                    }]
                }]
            }]
        }
        Client().put(url, content_type='application/json',
                     data=json.dumps(message))
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        self.assertEqual(4, len(args))
        args = list(reversed(args))   # switch to outside in
        self.assertTrue('99-1' in args[0])
        self.assertTrue('99-1' in args[1])
        self.assertTrue('99-1' in args[2])
        self.assertTrue('99-1-a' in args[0])
        self.assertTrue('99-1-a' in args[1])
        self.assertTrue('99-1-a' in args[2])
        self.assertTrue('99-1-a' in args[3])

    @patch('regcore_write.views.layer.db')
    def test_add_referenced(self, db):
        url = '/layer/layname/99/verver'

        message = {'99-1': [1, 2], '99-1-a': [3, 4], 'referenced': [5, 6]}
        db.Regulations.return_value.get.return_value = {
            'label': ['99'],
            'children': [{
                'label': ['99', 'Subpart', 'A'],
                'children': [{
                    'label': ['99', '1'],
                    'children': [{
                        'label': ['99', '1', 'a'],
                        'children': []
                    }]
                }]
            }]
        }
        Client().put(url, content_type='application/json',
                     data=json.dumps(message))
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        self.assertEqual(4, len(args))
        self.assertTrue('referenced' in args[0])
        self.assertTrue('referenced' in args[1])
        self.assertTrue('referenced' in args[2])
        self.assertTrue('referenced' in args[3])

    @patch('regcore_write.views.layer.db')
    def test_child_layers_no_results(self, db):
        db.Regulations.return_value.get.return_value = None
        self.assertEqual([], child_layers('layname', 'lll', 'vvv', {}))
        self.assertTrue(db.Regulations.return_value.get.called)
        self.assertEqual('lll',
                         db.Regulations.return_value.get.call_args[0][0])
        self.assertEqual('vvv',
                         db.Regulations.return_value.get.call_args[0][1])

    def test_child_label_of(self):
        self.assertTrue(child_label_of('1005-5-a-1-Interp-1',
                        '1005-5-Interp'))
