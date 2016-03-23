from django.test import TestCase

from regcore.layer import standardize_params


class LayerParamsTests(TestCase):
    def test_old_format(self):
        lp = standardize_params('label', 'version')
        self.assertEqual(lp.doc_type, 'cfr')
        self.assertEqual(lp.doc_id, 'version/label')
        self.assertEqual(lp.tree_id, 'label')

    def test_new_format(self):
        lp = standardize_params('cfr', 'version/label')
        self.assertEqual(lp.doc_type, 'cfr')
        self.assertEqual(lp.doc_id, 'version/label')
        self.assertEqual(lp.tree_id, 'label')

        lp = standardize_params('preamble', 'docid')
        self.assertEqual(lp.doc_type, 'preamble')
        self.assertEqual(lp.doc_id, 'docid')
        self.assertEqual(lp.tree_id, 'docid')
