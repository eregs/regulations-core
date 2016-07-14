import json
from unittest import TestCase

from django.test.client import Client
from mock import patch


class ViewsNoticeTest(TestCase):

    def test_add_not_json(self):
        url = '/notice/docdoc'

        response = Client().put(url, content_type='application/json',
                                data='{Invalid}')
        self.assertEqual(400, response.status_code)

    @patch('regcore_write.views.notice.storage')
    def test_add_label_success(self, storage):
        url = '/notice/docdoc'

        Client().put(url, content_type='application/json',
                     data=json.dumps({'some': 'struct'}))
        self.assertTrue(storage.for_notices.insert.called)
        args = storage.for_notices.insert.call_args[0]
        self.assertEqual('docdoc', args[0])
        self.assertEqual({'some': 'struct', 'cfr_parts': []}, args[1])

        Client().put(url, content_type='application/json',
                     data=json.dumps({'some': 'struct', 'cfr_part': '1111'}))
        self.assertTrue(storage.for_notices.insert.called)
        args = storage.for_notices.insert.call_args[0]
        self.assertEqual('docdoc', args[0])
        self.assertEqual({'some': 'struct', 'cfr_parts': ['1111']}, args[1])

        Client().put(
            url, content_type='application/json',
            data=json.dumps({'some': 'struct', 'cfr_parts': ['111', '222']}))
        self.assertTrue(storage.for_notices.insert.called)
        args = storage.for_notices.insert.call_args[0]
        self.assertEqual('docdoc', args[0])
        self.assertEqual({'some': 'struct', 'cfr_parts': ['111', '222']},
                         args[1])
