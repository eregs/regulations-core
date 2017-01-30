import json

from django.test import TestCase
from mock import patch


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
        storage.for_documents.bulk_delete.assert_called_with(
            'preamble', 'label', None,
        )
        storage.for_documents.bulk_insert.assert_called_with(
            [bulk_data], 'preamble', None,
        )
