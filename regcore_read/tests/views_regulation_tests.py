import json
from unittest import TestCase

from django.test.client import Client
from mock import patch

from regcore_read.views.regulation import *


class ViewsRegulationTest(TestCase):

    @patch('regcore_read.views.regulation.db')
    def test_get_good(self, db):
        url = '/regulation/lab/ver'
        db.Regulations.return_value.get.return_value = {"some": "thing"}
        response = Client().get(url)
        self.assertTrue(db.Regulations.return_value.get.called)
        args = db.Regulations.return_value.get.call_args[0]
        self.assertTrue('lab' in args)
        self.assertTrue('ver' in args)
        self.assertEqual(200, response.status_code)
        self.assertEqual({'some': 'thing'}, json.loads(response.content))

    @patch('regcore_read.views.regulation.db')
    def test_get_404(self, db):
        url = '/regulation/lab/ver'
        db.Regulations.return_value.get.return_value = None
        response = Client().get(url)
        self.assertTrue(db.Regulations.return_value.get.called)
        args = db.Regulations.return_value.get.call_args[0]
        self.assertTrue('lab' in args)
        self.assertTrue('ver' in args)
        self.assertEqual(404, response.status_code)

    @patch('regcore_read.views.regulation.db')
    def test_listing(self, db):
        url = '/regulation/lablab'
        db.Notices.return_value.listing.return_value = [
            {'document_number': '10', 'effective_on': '2010-10-10'},
            {'document_number': '15', 'effective_on': '2010-10-10'},
            {'document_number': '12'},
            {'document_number': '20', 'effective_on': '2011-11-11'},
            {'document_number': '25', 'effective_on': '2011-11-11'}
        ]
        db.Regulations.return_value.listing.return_value = [
            ('10', 'lablab'), ('15', 'lablab'), ('20', 'lablab')]

        response = Client().get(url)
        self.assertEqual(200, response.status_code)
        found = [False, False, False]
        for ver in json.loads(response.content)['versions']:
            if ver['version'] == '10' and 'by_date' not in ver:
                found[0] = True
            if ver['version'] == '15' and ver['by_date'] == '2010-10-10':
                found[1] = True
            if ver['version'] == '20' and ver['by_date'] == '2011-11-11':
                found[2] = True
        self.assertEqual(found, [True, True, True])

    @patch('regcore_read.views.regulation.db')
    def test_listing_all(self, db):
        url = '/regulation'
        db.Notices.return_value.listing.return_value = [
            {'document_number': '10', 'effective_on': '2010-10-10'},
            {'document_number': '15', 'effective_on': '2010-10-10'},
            {'document_number': '12'},
            {'document_number': '20', 'effective_on': '2011-11-11'},
            {'document_number': '25', 'effective_on': '2011-11-11'}
        ]
        db.Regulations.return_value.listing.return_value = [
            ('10', '1111'), ('15', '1111'), ('20', '1212')]

        response = Client().get(url)
        self.assertEqual(200, response.status_code)
        found = [False, False, False]
        for ver in json.loads(response.content)['versions']:
            if (ver['version'] == '10' and 'by_date' not in ver
                    and ver['regulation'] == '1111'):
                found[0] = True
            if (ver['version'] == '15' and ver['by_date'] == '2010-10-10'
                    and ver['regulation'] == '1111'):
                found[1] = True
            if (ver['version'] == '20' and ver['by_date'] == '2011-11-11'
                    and ver['regulation'] == '1212'):
                found[2] = True
        self.assertEqual(found, [True, True, True])
