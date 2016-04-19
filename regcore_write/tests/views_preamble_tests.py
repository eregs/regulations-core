import json
from mock import patch

from django.test import TestCase


class ViewsPreambleTests(TestCase):
    def test_invalid_json(self):
        """Only accepts valid JSON"""
        response = self.client.put(
            '/preamble/id_here', content_type='application/json',
            data='{Invalid}')
        self.assertEqual(400, response.status_code)

    @patch('regcore_write.views.document.storage')
    def test_stores(self, storage):
        """Stores any JSON it is given"""
        data = {
            'text': 'text',
            'label': ['label'],
            'children': [],
        }
        self.client.put(
            '/preamble/label',
            content_type='application/json',
            data=json.dumps(data),
        )
        bulk_data = dict(data)
        bulk_data['parent'] = None
        storage.for_documents.bulk_put.assert_called_with(
            [bulk_data], 'preamble', 'label', None,
        )
