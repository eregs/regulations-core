import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_write.views.diff import *


class ViewsDiffTest(TestCase):

    def test_add_not_json(self):
        url = '/diff/lablab/oldold/newnew'

        response = Client().put(url, content_type='application/json',
                                data='{Invalid}')
        self.assertEqual(400, response.status_code)

    @patch('regcore_write.views.diff.db')
    def test_add_label_success(self, db):
        url = '/diff/lablab/oldold/newnew'

        response = Client().put(url, content_type='application/json',
                                data=json.dumps({'some': 'struct'}))
        self.assertTrue(db.Diffs.return_value.put.called)
        args = db.Diffs.return_value.put.call_args[0]
        self.assertEqual(('lablab', 'oldold', 'newnew', {'some': 'struct'}),
                         args)
