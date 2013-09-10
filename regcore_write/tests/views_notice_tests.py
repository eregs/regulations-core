import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_write.views.notice import *


class ViewsNoticeTest(TestCase):

    def test_add_not_json(self):
        url = '/notice/docdoc'

        response = Client().put(url, content_type='application/json',
                                data='{Invalid}')
        self.assertEqual(400, response.status_code)

    @patch('regcore_write.views.notice.db')
    def test_add_label_success(self, db):
        url = '/notice/docdoc'

        response = Client().put(url, content_type='application/json',
                                data=json.dumps({'some': 'struct'}))
        self.assertTrue(db.Notices.return_value.put.called)
        args = db.Notices.return_value.put.call_args[0]
        self.assertEqual('docdoc', args[0])
        self.assertEqual({'some': 'struct'}, args[1])
