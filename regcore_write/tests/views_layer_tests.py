import json

from django.test import TestCase
from mock import patch

from regcore_write.views import layer


class ViewsLayerTest(TestCase):
    def put(self, data, name='layname', label='lablab', version='verver'):
        """Shorthand function for PUTing data to a view layer"""
        url = '/layer/{}/{}/{}'.format(name, label, version)
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
        response = self.put({'nonlab': []}, label='lablab')
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

        with patch('regcore_write.views.layer.db') as db:
            db.Regulations.return_value.get.return_value = root[0]
            self.put(message, **kwargs)
            self.assertTrue(db.Layers.return_value.bulk_put.called)
            layers_saved = db.Layers.return_value.bulk_put.call_args[0][0]
            return list(reversed(layers_saved))     # switch to outside in

    def test_add_success(self):
        """Can correctly add layer data when node is present in the db"""
        message = {
            'lablab': [1, 2],
            'lablab-b': [2, 3],
            'lablab-b-4': [3, 4],
        }
        l1, l2, l3 = self.put_with_mock_data(
            message, 'lablab', 'lablab-b', 'lablab-b-4')

        message['label'] = 'lablab'
        self.assertEqual(message, l1)

        #   Sub layers have fewer elements
        del message['lablab']
        message['label'] = 'lablab-b'
        self.assertEqual(message, l2)
        del message['lablab-b']
        message['label'] = 'lablab-b-4'
        self.assertEqual(message, l3)

    def test_add_skip_level(self):
        """Can correctly add layer data, even when skipping a node"""
        message = {
            'lablab': [1, 2],
            'lablab-b-4': [3, 4],
        }
        l1, l2, l3 = self.put_with_mock_data(
            message, 'lablab', 'lablab-b', 'lablab-b-4')

        message['label'] = 'lablab'
        self.assertEqual(message, l1)
        #   Sub layers have fewer elements
        del message['lablab']
        message['label'] = 'lablab-b'
        self.assertEqual(message, l2)
        message['label'] = 'lablab-b-4'
        self.assertEqual(message, l3)

    def test_add_interp_children(self):
        """Can correctly add layer data to interpretations"""
        message = {'99-5-Interp': [1, 2], '99-5-a-Interp': [3, 4]}
        layers_saved = self.put_with_mock_data(
            message, '99', '99-Interp', '99-5-Interp', '99-5-a-Interp',
            label='99')
        self.assertEqual(4, len(layers_saved))
        for saved in layers_saved:
            self.assertTrue('99-5-Interp' in saved)
            self.assertTrue('99-5-a-Interp' in saved)

    def test_add_subpart_children(self):
        """Can correctly add layer data to subparts"""
        message = {'99-1': [1, 2], '99-1-a': [3, 4]}
        l1, l2, l3, l4 = self.put_with_mock_data(
            message, '99', '99-Subpart-A', '99-1', '99-1-a', label='99')
        for saved in (l1, l2, l3):
            self.assertTrue('99-1' in saved)

        for saved in (l1, l2, l3, l4):
            self.assertTrue('99-1-a' in saved)

    def test_add_referenced(self):
        """The 'referenced' key is special; it should get added"""
        message = {'99-1': [1, 2], '99-1-a': [3, 4], 'referenced': [5, 6]}
        layers_saved = self.put_with_mock_data(
            message, '99', '99-Subpart-A', '99-1', '99-1-a', label='99')
        self.assertEqual(4, len(layers_saved))
        self.assertTrue(all('referenced' in saved for saved in layers_saved))

    @patch('regcore_write.views.layer.db')
    def test_child_layers_no_results(self, db):
        """If the db returns no regulation data, nothing should get saved"""
        db.Regulations.return_value.get.return_value = None
        self.assertEqual([], layer.child_layers('layname', 'lll', 'vvv', {}))
        self.assertTrue(db.Regulations.return_value.get.called)
        lab, ver = db.Regulations.return_value.get.call_args[0]
        self.assertEqual('lll', lab)
        self.assertEqual('vvv', ver)

    def test_child_label_of(self):
        """Correctly determine relationships between labels"""
        self.assertTrue(layer.child_label_of('1005-5-a-1-Interp-1',
                        '1005-5-Interp'))
