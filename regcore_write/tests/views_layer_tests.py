import json

from django.test import TestCase
from mock import patch

from regcore.layer import standardize_params
from regcore_write.views import layer


class ViewsLayerTest(TestCase):
    def put(self, data, name='layname', doc_type='cfr',
            doc_id='verver/lablab'):
        """Shorthand function for PUTing data to a view layer"""
        url = '/layer/{0}/{1}/{2}'.format(name, doc_type, doc_id)
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.client.put(url, content_type='application/json',
                               data=data)

    def test_add_not_json(self):
        """Non-JSON is invalid"""
        response = self.put('{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_label_mismatch(self):
        """Root label must match that found in the url"""
        response = self.put({'nonlab': []}, doc_id='verver/lablab')
        self.assertEqual(400, response.status_code)

    def put_with_mock_data(self, message, *labels, **kwargs):
        """Helper function to mock out the value returned from fetching the
        regulation from the database, then put the provided message, and
        return the response."""
        root = []
        children = root
        for label in labels:
            node = {'label': label.split('-'), 'children': []}
            children.append(node)
            children = node['children']

        with patch('regcore_write.views.layer.storage') as storage:
            storage.for_documents.get.return_value = root[0]
            self.put(message, **kwargs)
            self.assertTrue(storage.for_layers.bulk_insert.called)
            layers_saved = storage.for_layers.bulk_insert.call_args[0][0]
            return list(reversed(layers_saved))     # switch to outside in

    def test_add_success(self):
        """Can correctly add layer data when node is present in the db"""
        message = {
            'lablab': [1, 2],
            'lablab-b': [2, 3],
            'lablab-b-4': [3, 4],
        }
        l1, l2, l3 = self.put_with_mock_data(
            message, 'lablab', 'lablab-b', 'lablab-b-4', doc_type='cfr',
            doc_id='verver/lablab')

        message['doc_id'] = 'verver/lablab'
        self.assertEqual(message, l1)

        #   Sub layers have fewer elements
        del message['lablab']
        message['doc_id'] = 'verver/lablab-b'
        self.assertEqual(message, l2)
        del message['lablab-b']
        message['doc_id'] = 'verver/lablab-b-4'
        self.assertEqual(message, l3)

    def test_add_skip_level(self):
        """Can correctly add layer data, even when skipping a node"""
        message = {
            'lablab': [1, 2],
            'lablab-b-4': [3, 4],
        }
        l1, l2, l3 = self.put_with_mock_data(
            message, 'lablab', 'lablab-b', 'lablab-b-4')

        message['doc_id'] = 'verver/lablab'
        self.assertEqual(message, l1)
        #   Sub layers have fewer elements
        del message['lablab']
        message['doc_id'] = 'verver/lablab-b'
        self.assertEqual(message, l2)
        message['doc_id'] = 'verver/lablab-b-4'
        self.assertEqual(message, l3)

    def test_add_interp_children(self):
        """Can correctly add layer data to interpretations"""
        message = {'99-5-Interp': [1, 2], '99-5-a-Interp': [3, 4]}
        l1, l2, l3, l4 = self.put_with_mock_data(
            message, '99', '99-Interp', '99-5-Interp', '99-5-a-Interp',
            doc_id='verver/99')
        for saved in (l1, l2, l3):
            self.assertIn('99-5-Interp', saved)
            self.assertIn('99-5-a-Interp', saved)
        self.assertNotIn('99-5-Interp', l4)
        self.assertIn('99-5-a-Interp', l4)

    def test_add_subpart_children(self):
        """Can correctly add layer data to subparts"""
        message = {'99-1': [1, 2], '99-1-a': [3, 4]}
        l1, l2, l3, l4 = self.put_with_mock_data(
            message, '99', '99-Subpart-A', '99-1', '99-1-a',
            doc_id='verver/99')
        for saved in (l1, l2, l3):
            self.assertIn('99-1', saved)
            self.assertIn('99-1-a', saved)
        self.assertNotIn('99-1', l4)
        self.assertIn('99-1-a', l4)

    def test_add_referenced(self):
        """The 'referenced' key is special; it should get added"""
        message = {'99-1': [1, 2], '99-1-a': [3, 4], 'referenced': [5, 6]}
        layers_saved = self.put_with_mock_data(
            message, '99', '99-Subpart-A', '99-1', '99-1-a',
            doc_id='verver/99')
        self.assertEqual(4, len(layers_saved))
        self.assertTrue(all('referenced' in saved for saved in layers_saved))

    @patch('regcore_write.views.layer.storage')
    def test_add_preamble_layer(self, storage):
        """If adding layer data to a preamble, we should see layers saved for
        each level of the preamble tree. This requires we construct a fake
        preamble."""
        storage.for_documents.get.return_value = None
        storage.for_documents.get.return_value = dict(
            label=['111_22'], children=[
                dict(label=['111_22', '1'], children=[]),
                dict(label=['111_22', '2'], children=[
                    dict(label=['111_22', '2', 'a'], children=[])]),
                dict(label=['111_22', '3'], children=[
                    dict(label=['111_22', '3', 'a'], children=[
                        dict(label=['111_22', '3', 'a', 'i'], children=[])]),
                    dict(label=['111_22', '3', 'b'], children=[
                        dict(label=['111_22', '3', 'b', 'i'], children=[])])
                ])])
        message = {'111_22': 'layer1', '111_22-3': 'layer2',
                   '111_22-3-b': 'layer3'}
        self.client.put('/layer/aname/preamble/111_22',
                        data=json.dumps(message))
        stored = storage.for_layers.bulk_insert.call_args[0][0]
        self.assertEqual(len(stored), 9)
        for label in ('111_22-1', '111_22-2', '111_22-2-a', '111_22-3-a',
                      '111_22-3-a-i', '111_22-3-b-i'):
            self.assertIn({'doc_id': label}, stored)     # i.e. empty
        self.assertIn({'doc_id': '111_22', '111_22': 'layer1',
                       '111_22-3': 'layer2', '111_22-3-b': 'layer3'}, stored)
        self.assertIn({'doc_id': '111_22-3', '111_22-3': 'layer2',
                       '111_22-3-b': 'layer3'}, stored)
        self.assertIn({'doc_id': '111_22-3-b', '111_22-3-b': 'layer3'},
                      stored)

    @patch('regcore_write.views.layer.storage')
    def test_child_layers_no_results(self, storage):
        """If the db returns no regulation data, nothing should get saved"""
        storage.for_documents.get.return_value = None
        layer_params = standardize_params('cfr', 'vvv/lll')
        self.assertEqual([], layer.child_layers(layer_params, {}))
        self.assertTrue(storage.for_documents.get.called)
        storage.for_documents.get.assert_called_with('cfr', 'lll', 'vvv')

        storage.for_documents.get.return_value = None
        layer_params = standardize_params('preamble', 'docdoc')
        self.assertEqual([], layer.child_layers(layer_params, {}))
        storage.for_documents.get.assert_called_with('preamble', 'docdoc')

    def test_child_label_of(self):
        """Correctly determine relationships between labels"""
        self.assertTrue(layer.child_label_of('1005-5-a-1-Interp-1',
                        '1005-5-Interp'))
