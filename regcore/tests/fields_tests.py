from unittest import TestCase

from regcore.fields import CompressedJSONField


class CompressesJSONFieldTest(TestCase):
    def test_short_json(self):
        """Short JSON strings shouldn't get compressed, but should be
        invertible"""
        field = CompressedJSONField()
        to_store = field.get_prep_value({'a': 'dictionary'})
        self.assertEqual(to_store[:2], 'j$')
        self.assertIn('dictionary', to_store)

        from_store = field.to_python(to_store)
        self.assertEqual(from_store, {'a': 'dictionary'})

    def test_long_json(self):
        """Long JSON objects _do_ get compressed, in addition to being
        invertible"""
        field = CompressedJSONField()
        value = {'key': 'value'*1000}
        to_store = field.get_prep_value(value)
        self.assertEqual(to_store[:4], 'jb6$')
        self.assertNotIn('value', to_store)     # because it's been compressed
        self.assertTrue(len(to_store) < 1000)

        from_store = field.to_python(to_store)
        self.assertEqual(from_store, value)
