import json
from unittest import TestCase

from django.test.client import Client
from mock import patch


class ViewsRegulationTest(TestCase):
    @patch('regcore_read.views.document.storage')
    def test_get_good(self, storage):
        url = '/regulation/lab/ver'
        storage.for_documents.get.return_value = {"some": "thing"}
        response = Client().get(url)
        self.assertTrue(storage.for_documents.get.called)
        args = storage.for_documents.get.call_args[0]
        self.assertIn('lab', args)
        self.assertIn('ver', args)
        self.assertEqual(200, response.status_code)
        self.assertEqual({'some': 'thing'},
                         json.loads(response.content.decode('utf-8')))

    @patch('regcore_read.views.document.storage')
    def test_get_empty(self, storage):
        url = '/regulation/lab/ver'
        storage.for_documents.get.return_value = {}
        response = Client().get(url)
        self.assertTrue(storage.for_documents.get.called)
        args = storage.for_documents.get.call_args[0]
        self.assertIn('lab', args)
        self.assertIn('ver', args)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.content.decode('utf-8')))

    @patch('regcore_read.views.document.storage')
    def test_get_404(self, storage):
        url = '/regulation/lab/ver'
        storage.for_documents.get.return_value = None
        response = Client().get(url)
        self.assertTrue(storage.for_documents.get.called)
        args = storage.for_documents.get.call_args[0]
        self.assertIn('lab', args)
        self.assertIn('ver', args)
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.document.storage')
    def test_listing(self, storage):
        url = '/regulation/lablab'
        storage.for_notices.listing.return_value = [
            {'document_number': '10', 'effective_on': '2010-10-10'},
            {'document_number': '15', 'effective_on': '2010-10-10'},
            {'document_number': '12'},
            {'document_number': '20', 'effective_on': '2011-11-11'},
            {'document_number': '25', 'effective_on': '2011-11-11'}
        ]
        storage.for_documents.listing.return_value = [
            ('10', 'lablab'), ('15', 'lablab'), ('20', 'lablab')]

        response = Client().get(url)
        self.assertEqual(200, response.status_code)
        found = [False, False, False]
        for ver in json.loads(response.content.decode('utf-8'))['versions']:
            if ver['version'] == '10' and 'by_date' not in ver:
                found[0] = True
            if ver['version'] == '15' and ver['by_date'] == '2010-10-10':
                found[1] = True
            if ver['version'] == '20' and ver['by_date'] == '2011-11-11':
                found[2] = True
        self.assertEqual(found, [True, True, True])

    @patch('regcore_read.views.document.storage')
    def test_listing_all(self, storage):
        url = '/regulation'
        storage.for_notices.listing.return_value = [
            {'document_number': '10', 'effective_on': '2010-10-10'},
            {'document_number': '15', 'effective_on': '2010-10-10'},
            {'document_number': '12'},
            {'document_number': '20', 'effective_on': '2011-11-11'},
            {'document_number': '25', 'effective_on': '2011-11-11'}
        ]
        storage.for_documents.listing.return_value = [
            ('10', '1111'), ('15', '1111'), ('20', '1212')]

        response = Client().get(url)
        self.assertEqual(200, response.status_code)
        found = [False, False, False]
        for ver in json.loads(response.content.decode('utf-8'))['versions']:
            if (ver['version'] == '10' and 'by_date' not in ver and
                    ver['regulation'] == '1111'):
                found[0] = True
            if (ver['version'] == '15' and ver['by_date'] == '2010-10-10' and
                    ver['regulation'] == '1111'):
                found[1] = True
            if (ver['version'] == '20' and ver['by_date'] == '2011-11-11' and
                    ver['regulation'] == '1212'):
                found[2] = True
        self.assertEqual(found, [True, True, True])
