import json
from unittest import TestCase

from regcore.responses import success, user_error


class ResponsesTest(TestCase):

    def test_user_error(self):
        response = user_error("my reason")
        self.assertEqual(400, response.status_code)
        self.assertEqual('application/json', response['Content-type'])
        response_text = response.content.decode('utf-8')
        self.assertIn('my reason', response_text)
        json.loads(response_text)   # valid json

    def test_success_empty(self):
        response = success()
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(response.content))

    def test_success_full(self):
        structure = {'some': {'structure': 1}}
        response = success(structure)
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response['Content-type'])
        self.assertEqual(structure,
                         json.loads(response.content.decode('utf-8')))
