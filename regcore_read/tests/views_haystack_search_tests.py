from collections import namedtuple

from django.test import TestCase
from django.test.client import Client
from mock import Mock, patch

from regcore.search_indexes import RegulationIndex
from regcore_read.views.haystack_search import *


class ViewsHaystackSearchTest(TestCase):
    urls = 'regcore_read.tests.urls'

    def test_search_missing_q(self):
        response = Client().get('/haystack_search?non_q=test')
        self.assertEqual(400, response.status_code)

    @patch('regcore_read.views.haystack_search.SearchQuerySet')
    def test_search_success(self, sqs):
        results = sqs.return_value.models.return_value.filter
        results.return_value = []
        response = Client().get('/haystack_search?q=test')
        self.assertEqual(200, response.status_code)
        self.assertTrue(results.called)

    @patch('regcore_read.views.haystack_search.SearchQuerySet')
    def test_search_version(self, sqs):
        results = sqs.return_value.models.return_value.filter
        version_filter = results.return_value.filter
        version_filter.return_value = []
        response = Client().get('/haystack_search?q=test&version=12345678')
        self.assertEqual(200, response.status_code)
        self.assertTrue(version_filter.called)
        self.assertEqual('12345678', version_filter.call_args[1]['version'])

    @patch('regcore_read.views.haystack_search.SearchQuerySet')
    def test_search_version_regulation(self, sqs):
        results = sqs.return_value.models.return_value.filter
        version_filter = results.return_value.filter
        regulation_filter = version_filter.return_value.filter

        regulation_filter.return_value = []
        response = Client().get('/haystack_search?q=test&'
                                + 'version=678&regulation=123')
        self.assertEqual(200, response.status_code)
        self.assertTrue(regulation_filter.called)
        self.assertEqual('678', version_filter.call_args[1]['version'])
        self.assertEqual('123', regulation_filter.call_args[1]['regulation'])

    @patch('regcore_read.views.haystack_search.SearchQuerySet')
    @patch('regcore_read.views.haystack_search.transform_results')
    def test_search_paging(self, transform_results, sqs):
        results = sqs.return_value.models.return_value.filter
        results.return_value = list(range(500))
        transform_results.return_value = {}
        response = Client().get('/haystack_search?q=test&page=5')
        self.assertEqual(200, response.status_code)
        self.assertTrue(results.called)
        self.assertTrue(transform_results.called)
        self.assertEqual(list(range(250, 300)),
                         transform_results.call_args[0][0])

    @patch('regcore_read.views.haystack_search.db')
    def test_transform_results(self, db):
        # combine keyterms and terms into a single layer
        db.Layers.return_value.get.return_value = {
            '2': [{'key_term': 'k2'}], '3': [{'key_term': 'k3'}],
            '6': [{'key_term': 'k6'}], '7': [{'key_term': 'k7'}],
            'referenced': {
                'lab1': {'reference': '1', 'term': 'd1'},
                'lab2': {'reference': '3', 'term': 'd3'},
                'lab3': {'reference': '5', 'term': 'd5'},
                'lab4': {'reference': '7', 'term': 'd7'}
            }
        }

        Result = namedtuple('Result', ('regulation', 'version',
                                       'label_string', 'text', 'title'))
        results = transform_results([
            Result('r', 'v', '0', '', []),
            Result('rr', 'v', '1', '', []),
            Result('r', 'vv', '2', '', []),
            Result('r', 'v', '3', '', []),
            Result('rr', 'vv', '4', '', ['t4']),
            Result('r', 'vv', '5', '', ['t5']),
            Result('rr', 'v', '6', '', ['t6']),
            Result('r', 'v', '7', '', ['t7']),
        ])

        self.assertFalse('title' in results[0])
        self.assertEqual('d1', results[1]['title'])
        self.assertEqual('k2', results[2]['title'])
        self.assertEqual('k3', results[3]['title'])
        self.assertEqual('t4', results[4]['title'])
        self.assertEqual('t5', results[5]['title'])
        self.assertEqual('t6', results[6]['title'])
        self.assertEqual('t7', results[7]['title'])
