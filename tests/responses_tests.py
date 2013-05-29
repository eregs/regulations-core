from core import app
from core.responses import *
from flasktest import FlaskTest
import json
from unittest import TestCase

class ResponsesTest(TestCase):

    @FlaskTest.withContext
    def test_user_error(self):
        response = user_error("my reason")
        self.assertEqual(400, response.status_code)
        self.assertEqual('application/json',
            response.headers['Content-type'])
        self.assertTrue('my reason' in response.data)
        json.loads(response.data)   #   valid json

    @FlaskTest.withContext
    def test_success_empty(self):
        response = success()
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(response.data))

    @FlaskTest.withContext
    def test_success_full(self):
        structure = {'some': {'structure': 1}}
        response = success(structure)
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response.headers['Content-type'])
        self.assertEqual(structure, json.loads(response.data))

