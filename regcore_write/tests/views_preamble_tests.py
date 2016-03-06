from django.test import TestCase
from mock import patch


class ViewsPreambleTests(TestCase):
    def test_invalid_json(self):
        """Only accepts valid JSON"""
        response = self.client.put(
            '/preamble/id_here', content_type='application/json',
            data='{Invalid}')
        self.assertEqual(400, response.status_code)

    @patch('regcore_write.views.preamble.storage')
    def test_stores(self, storage):
        """Stores any JSON it is given"""
        self.client.put('/preamble/id_here', content_type='application/json',
                        data='{"some": "data"}')
        self.assertTrue(storage.for_preambles.put.called)
        self.assertEqual(storage.for_preambles.put.call_args[0],
                         ('id_here', {'some': 'data'}))
