from datetime import date

from django.test import TestCase
import six

from regcore.db.django_models import (
    DMDiffs, DMLayers, DMNotices, DMPreambles, DMRegulations)
from regcore.models import Diff, Layer, Notice, Preamble, Regulation


class DMRegulationsTest(TestCase):
    def setUp(self):
        self.dmr = DMRegulations()

    def test_get_404(self):
        self.assertIsNone(self.dmr.get('lablab', 'verver'))

    def test_get_success(self):
        Regulation(version='verver', label_string='a-b', text='ttt',
                   node_type='tyty', children=[]).save()
        self.assertEqual({'text': 'ttt',
                          'label': ['a', 'b'],
                          'children': [],
                          'node_type': 'tyty'}, self.dmr.get('a-b', 'verver'))

    def test_listing(self):
        Regulation(version='ver1', label_string='a-b', text='textex',
                   node_type='ty', children=[]).save()
        Regulation(version='aaa', label_string='a-b', text='textex',
                   node_type='ty', children=[]).save()
        Regulation(version='333', label_string='a-b', text='textex',
                   node_type='ty', children=[]).save()
        Regulation(version='four', label_string='a-b', text='textex',
                   node_type='ty', children=[]).save()

        results = self.dmr.listing('a-b')
        self.assertEqual([('333', 'a-b'), ('aaa', 'a-b'), ('four', 'a-b'),
                          ('ver1', 'a-b')], results)

        Regulation(version='ver1', label_string='1111', text='aaaa',
                   node_type='ty', root=True, children=[]).save()
        Regulation(version='ver2', label_string='1111', text='bbbb',
                   node_type='ty', root=True, children=[]).save()
        Regulation(version='ver3', label_string='1111', text='cccc',
                   node_type='ty', root=False, children=[]).save()

        results = self.dmr.listing()
        self.assertEqual([('ver1', '1111'), ('ver2', '1111')], results)

    def test_bulk_put(self):
        """Writing multiple documents should save correctly. They can be
        modified"""
        n2 = {'text': 'some text', 'label': ['111', '2'], 'children': [],
              'node_type': 'tyty'}
        n3 = {'text': 'other', 'label': ['111', '3'], 'children': [],
              'node_type': 'tyty2'}
        root = {'text': 'root', 'label': ['111'], 'node_type': 'tyty3',
                'children': [n2, n3]}
        nodes = [root, n2, n3]
        self.dmr.bulk_put(nodes, 'verver', '111')

        expected_root = {
            'version': 'verver', 'label_string': '111', 'text': 'root',
            'title': '', 'node_type': 'tyty3', 'children': [n2, n3],
            'root': True}
        expected_n2 = {
            'version': 'verver', 'label_string': '111-2', 'text': 'some text',
            'title': '', 'node_type': 'tyty', 'children': [], 'root': False}
        expected_n3 = {
            'version': 'verver', 'label_string': '111-3', 'text': 'other',
            'title': '', 'node_type': 'tyty2', 'children': [], 'root': False}
        fields = expected_root.keys()
        six.assertCountEqual(self, Regulation.objects.all().values(*fields),
                             [expected_root, expected_n2, expected_n3])

        root['title'] = 'New Title'
        self.dmr.bulk_put(nodes, 'verver', '111')

        expected_root['title'] = 'New Title'
        six.assertCountEqual(self, Regulation.objects.all().values(*fields),
                             [expected_root, expected_n2, expected_n3])


class DMLayersTest(TestCase):
    def setUp(self):
        self.dml = DMLayers()

    def test_get_404(self):
        self.assertIsNone(self.dml.get('namnam', 'lablab', 'verver'))

    def test_get_success(self):
        Layer(version='verver', name='namnam', label='lablab',
              layer={"some": "body"}).save()

        self.assertEqual({"some": 'body'},
                         self.dml.get('namnam', 'lablab', 'verver'))

    def test_bulk_put(self):
        """Writing multiple documents should save correctly. They can be
        modified"""
        layers = [
            {'111-22': [], '111-22-a': [], 'label': '111-22'},
            {'111-23': [], 'label': '111-23'}]
        self.dml.bulk_put(layers, 'verver', 'name', '111')

        expected = [
            {'version': 'verver', 'name': 'name', 'label': '111-22',
             'layer': {'111-22': [], '111-22-a': []}},
            {'version': 'verver', 'name': 'name', 'label': '111-23',
             'layer': {'111-23': []}}]
        fields = expected[0].keys()
        six.assertCountEqual(self, Layer.objects.all().values(*fields),
                             expected)

        layers[1] = {'111-23': [1], 'label': '111-23'}
        self.dml.bulk_put(layers, 'verver', 'name', '111')

        expected[1]['layer'] = {'111-23': [1]}
        six.assertCountEqual(self, Layer.objects.all().values(*fields),
                             expected)


class DMNoticesTest(TestCase):
    def setUp(self):
        self.dmn = DMNotices()

    def test_get_404(self):
        self.assertIsNone(self.dmn.get('docdoc'))

    def test_get_success(self):
        Notice(document_number='docdoc', fr_url='frfr',
               publication_date=date.today(),
               notice={"some": "body"}).save()
        self.assertEqual({"some": 'body'}, self.dmn.get('docdoc'))

    def test_listing(self):
        n = Notice(document_number='22', fr_url='fr1', notice={},
                   effective_on=date(2005, 5, 5),
                   publication_date=date(2001, 3, 3))
        n.save()
        n.noticecfrpart_set.create(cfr_part='876')
        n = Notice(document_number='9', fr_url='fr2', notice={},
                   publication_date=date(1999, 1, 1))
        n.noticecfrpart_set.create(cfr_part='876')
        n.noticecfrpart_set.create(cfr_part='111')
        n.save()

        self.assertEqual([{'document_number': '22', 'fr_url': 'fr1',
                           'publication_date': '2001-03-03',
                           'effective_on': '2005-05-05'},
                          {'document_number': '9', 'fr_url': 'fr2',
                           'publication_date': '1999-01-01'}],
                         self.dmn.listing())

        self.assertEqual(self.dmn.listing(), self.dmn.listing('876'))
        self.assertEqual([], self.dmn.listing('888'))

    def test_put(self):
        """We can insert and replace a notice"""
        doc = {"some": "structure",
               'effective_on': '2011-01-01',
               'fr_url': 'http://example.com',
               'publication_date': '2010-02-02',
               'cfr_parts': ['222']}
        self.dmn.put('docdoc', doc)

        expected = {"document_number": "docdoc",
                    "effective_on": date(2011, 1, 1),
                    "fr_url": "http://example.com",
                    "publication_date": date(2010, 2, 2),
                    "noticecfrpart__cfr_part": '222',
                    "notice": doc}
        fields = expected.keys()
        six.assertCountEqual(self, Notice.objects.all().values(*fields),
                             [expected])

        doc['fr_url'] = 'url2'
        self.dmn.put('docdoc', doc)

        expected['fr_url'] = 'url2'
        six.assertCountEqual(self, Notice.objects.all().values(*fields),
                             [expected])


class DMDiffTest(TestCase):
    def setUp(self):
        self.dmd = DMDiffs()

    def test_get_404(self):
        self.assertIsNone(self.dmd.get('lablab', 'oldold', 'newnew'))

    def test_get_success(self):
        Diff(label='lablab', old_version='oldold', new_version='newnew',
             diff={"some": "body"}).save()

        self.assertEqual({"some": 'body'},
                         self.dmd.get('lablab', 'oldold', 'newnew'))

    def test_put(self):
        """We can insert and replace a diff"""
        self.dmd.put('lablab', 'oldold', 'newnew', {"some": "structure"})

        expected = {"label": "lablab", "old_version": "oldold",
                    "new_version": "newnew", "diff": {"some": "structure"}}
        fields = expected.keys()
        six.assertCountEqual(self, Diff.objects.all().values(*fields),
                             [expected])

        self.dmd.put('lablab', 'oldold', 'newnew', {"other": "structure"})
        expected['diff'] = {'other': 'structure'}
        six.assertCountEqual(self, Diff.objects.all().values(*fields),
                             [expected])


class DMPreambleTest(TestCase):
    def test_get(self):
        """Can fetch preamble docs"""
        self.assertIsNone(DMPreambles().get('docdoc'))

        Preamble(document_number='docdocdoc', data={'some': 'data'}).save()
        self.assertEqual({"some": 'data'}, DMPreambles().get('docdocdoc'))

    def test_put(self):
        """We can insert and replace a pramble"""
        DMPreambles().put('docdoc', {'some': 'struct', 'here': True})

        expected = {'document_number': 'docdoc',
                    'data': {'some': 'struct', 'here': True}}
        fields = expected.keys()
        six.assertCountEqual(self, Preamble.objects.all().values(*fields),
                             [expected])

        DMPreambles().put('docdoc', {'other': 1})
        expected['data'] = {'other': 1}
        six.assertCountEqual(self, Preamble.objects.all().values(*fields),
                             [expected])
