import json

from django.test import TestCase
from mock import patch


class ViewsPreambleTests(TestCase):
    @patch('regcore_read.views.document.storage')
    def test_get(self, storage):
        """We should only give a 404 when we have *no* result. Otherwise,
        return the retrieved (possible empty) doc"""
        storage.for_documents.get.return_value = None
        self.assertEqual(404, self.client.get('/preamble/docdoc').status_code)

        storage.for_documents.get.return_value = {}
        response = self.client.get('/preamble/docdoc')
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.content.decode('utf-8')))

        storage.for_documents.get.return_value = {'slightly': 'complex'}
        response = self.client.get('/preamble/docdoc')
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'slightly': 'complex'})
