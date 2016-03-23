from django.test import TestCase

from regcore.layer import LayerParams


class LayerParamsTests(TestCase):
    def test_old_format(self):
        lp = LayerParams('label', 'version')
        self.assertEqual(lp.doc_type, 'cfr')
        self.assertEqual(lp.doc_id, 'version/label')
        self.assertEqual(lp.tree_id, 'label')

    def test_new_format(self):
        lp = LayerParams('cfr', 'version/label')
        self.assertEqual(lp.doc_type, 'cfr')
        self.assertEqual(lp.doc_id, 'version/label')
        self.assertEqual(lp.tree_id, 'label')

        lp = LayerParams('preamble', 'docid')
        self.assertEqual(lp.doc_type, 'preamble')
        self.assertEqual(lp.doc_id, 'docid')
        self.assertEqual(lp.tree_id, 'docid')
