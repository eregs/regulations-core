import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_read.views.notice import *


class ViewsNoticeTest(TestCase):
    @patch('regcore_read.views.notice.db')
    def test_get_none(self, db):
        db.Notices.return_value.get.return_value = None
        response = Client().get('/notice/docdoc')
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.notice.db')
    def test_get_empty(self, db):
        db.Notices.return_value.get.return_value = {}
        response = Client().get('/notice/docdoc')
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.content))

    @patch('regcore_read.views.notice.db')
    def test_get_results(self, db):
        db.Notices.return_value.get.return_value = {'example': 'response'}
        response = Client().get('/notice/docdoc')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content))

    @patch('regcore_read.views.notice.db')
    def test_listing(self, db):
        db.Notices.return_value.listing.return_value = [1, 2, 3]
        response = Client().get('/notice')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'results': [1, 2, 3]},
                         json.loads(response.content))
