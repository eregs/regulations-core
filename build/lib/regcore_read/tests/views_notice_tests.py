import json
from unittest import TestCase

from django.test.client import Client
from mock import patch


class ViewsNoticeTest(TestCase):
    @patch('regcore_read.views.notice.storage')
    def test_get_none(self, storage):
        storage.for_notices.get.return_value = None
        response = Client().get('/notice/docdoc')
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.notice.storage')
    def test_get_empty(self, storage):
        storage.for_notices.get.return_value = {}
        response = Client().get('/notice/docdoc')
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.content.decode('utf-8')))

    @patch('regcore_read.views.notice.storage')
    def test_get_results(self, storage):
        storage.for_notices.get.return_value = {'example': 'response'}
        response = Client().get('/notice/docdoc')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content.decode('utf-8')))

    @patch('regcore_read.views.notice.storage')
    def test_listing(self, storage):
        storage.for_notices.listing.return_value = [1, 2, 3]
        response = Client().get('/notice')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'results': [1, 2, 3]},
                         json.loads(response.content.decode('utf-8')))
