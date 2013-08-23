from regcore.index import *
from mock import patch
from pyelasticsearch.exceptions import IndexAlreadyExistsError
from unittest import TestCase


class IndexTest(TestCase):

    @patch('regcore.index.ElasticSearch')
    def test_init_schema(self, es):
        init_schema()
        self.assertTrue(es.called)
        self.assertTrue(es.return_value.create_index.called)
        self.assertTrue(es.return_value.put_mapping.called)

    @patch('regcore.index.ElasticSearch')
    def test_init_schema_index_exists(self, es):
        es.return_value.create_index.side_effect = IndexAlreadyExistsError()
        init_schema()
        self.assertTrue(es.return_value.put_mapping.called)
