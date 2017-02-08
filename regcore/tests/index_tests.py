from unittest import TestCase

from mock import patch
from pyelasticsearch.exceptions import IndexAlreadyExistsError

from regcore.index import init_schema


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
