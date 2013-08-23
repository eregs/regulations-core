import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore.views.notice import *


class ViewsNoticeTest(TestCase):

    def test_add_not_json(self):
        url = '/notice/docdoc'

        response = Client().put(url, content_type='application/json',
                                data='{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_post(self):
        url = '/notice/docdoc'

        response = Client().post(url, content_type='application/json',
                                 data=json.dumps({'some': 'struct'}))
        self.assertEqual(405, response.status_code)

    @patch('regcore.views.notice.db')
    def test_add_label_success(self, db):
        url = '/notice/docdoc'

        response = Client().put(url, content_type='application/json',
                                data=json.dumps({'some': 'struct'}))
        self.assertTrue(db.Notices.return_value.put.called)
        args = db.Notices.return_value.put.call_args[0]
        self.assertEqual('docdoc', args[0])
        self.assertEqual({'some': 'struct'}, args[1])

    @patch('regcore.views.notice.db')
    def test_get_none(self, db):
        db.Notices.return_value.get.return_value = None
        response = Client().get('/notice/docdoc')
        self.assertEqual(404, response.status_code)

    @patch('regcore.views.notice.db')
    def test_get_results(self, db):
        db.Notices.return_value.get.return_value = {'example': 'response'}
        response = Client().get('/notice/docdoc')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'},
                         json.loads(response.content))

    @patch('regcore.views.notice.db')
    def test_listing(self, db):
        db.Notices.return_value.listing.return_value = [1, 2, 3]
        response = Client().get('/notice')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'results': [1, 2, 3]},
                         json.loads(response.content))
