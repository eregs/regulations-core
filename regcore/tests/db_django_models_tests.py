import copy
from datetime import date

from django.test import TestCase
import six

from regcore.db.django_models import DMDiffs, DMLayers, DMNotices, DMDocuments
from regcore.models import Diff, Layer, Notice, Document


class DMDocumentsTest(TestCase):
    def setUp(self):
        self.dmr = DMDocuments()

    def test_get_404(self):
        self.assertIsNone(self.dmr.get('lablab', 'verver'))

    def test_get_cfr(self):
        Document(doc_type='cfr', version='verver', label_string='a-b',
                 text='ttt', node_type='tyty').save()
        self.assertEqual(
            {
                'text': 'ttt',
                'label': ['a', 'b'],
                'lft': 1,
                'children': [],
                'node_type': 'tyty'
            },
            self.dmr.get('cfr', 'a-b', 'verver'),
        )

    def test_get_preamble(self):
        Document(doc_type='preamble', version='verver', label_string='a-b',
                 text='ttt', node_type='tyty').save()
        self.assertEqual(
            {
                'text': 'ttt',
                'label': ['a', 'b'],
                'lft': 1,
                'children': [],
                'node_type': 'tyty'
            },
            self.dmr.get('preamble', 'a-b', 'verver'),
        )

    def test_listing(self):
        Document(id='ver1-a-b', doc_type='cfr', version='ver1',
                 label_string='a-b', text='textex', node_type='ty').save()
        Document(id='aaa-a-b', doc_type='cfr', version='aaa',
                 label_string='a-b', text='textex', node_type='ty').save()
        Document(id='333-a-b', doc_type='cfr', version='333',
                 label_string='a-b', text='textex', node_type='ty').save()
        Document(id='four-a-b', doc_type='cfr', version='four',
                 label_string='a-b', text='textex', node_type='ty').save()

        results = self.dmr.listing('cfr', 'a-b')
        self.assertEqual([('333', 'a-b'), ('aaa', 'a-b'), ('four', 'a-b'),
                          ('ver1', 'a-b')], results)

        Document(id='ver1-1111', doc_type='cfr', version='ver1',
                 label_string='1111', text='aaaa', node_type='ty',
                 root=True).save()
        Document(id='ver2-1111', doc_type='cfr', version='ver2',
                 label_string='1111', text='bbbb', node_type='ty',
                 root=True).save()
        Document(id='ver3-1111', doc_type='cfr', version='ver3',
                 label_string='1111', text='cccc', node_type='ty',
                 root=False).save()

        results = self.dmr.listing('cfr')
        self.assertEqual([('ver1', '1111'), ('ver2', '1111')], results)

    def test_bulk_put(self):
        """Writing multiple documents should save correctly. They can be
        modified. The lft and rght ids assigned by the Modified Preorder Tree
        Traversal algorithm are shown below:

                                (1)root(6)
                                /    \
                               /       \
                         (2)n2(3)    (4)n3(5)
        """
        n2 = {'text': 'some text', 'label': ['111', '2'], 'lft': 2,
              'children': [], 'node_type': 'tyty'}
        n3 = {'text': 'other', 'label': ['111', '3'], 'children': [], 'lft': 4,
              'node_type': 'tyty2'}
        root = {'text': 'root', 'label': ['111'], 'lft': 1,
                'node_type': 'tyty3', 'children': [n2, n3]}
        original = copy.deepcopy(root)
        n2['parent'] = root
        n3['parent'] = root
        nodes = [root, n2, n3]
        self.dmr.bulk_put(nodes, 'cfr', 'verver')
        self.assertEqual(DMDocuments().get('cfr', '111', 'verver'), original)

        root['title'] = original['title'] = 'New Title'
        self.dmr.bulk_delete('cfr', '111', 'verver')
        self.dmr.bulk_put(nodes, 'cfr', 'verver')

        self.assertEqual(DMDocuments().get('cfr', '111', 'verver'), original)


class DMLayersTest(TestCase):
    def setUp(self):
        self.dml = DMLayers()

    def test_get_404(self):
        self.assertIsNone(self.dml.get('namnam', 'cfr', 'verver/lablab'))

    def test_get_success(self):
        Layer(name='namnam', doc_type='cfr', doc_id='verver/lablab',
              layer={"some": "body"}).save()

        self.assertEqual({"some": 'body'},
                         self.dml.get('namnam', 'cfr', 'verver/lablab'))

    def test_bulk_put(self):
        """Writing multiple documents should save correctly. They can be
        modified"""
        layers = [{'111-22': [], '111-22-a': [], 'doc_id': 'verver/111-22'},
                  {'111-23': [], 'doc_id': 'verver/111-23'}]
        self.dml.bulk_put(layers, 'name', 'cfr')

        self.assertEqual(Layer.objects.count(), 2)
        self.assertEqual(self.dml.get('name', 'cfr', 'verver/111-22'),
                         {'111-22': [], '111-22-a': []})
        self.assertEqual(self.dml.get('name', 'cfr', 'verver/111-23'),
                         {'111-23': []})

        layers[1] = {'111-23': [1], 'doc_id': 'verver/111-23'}
        self.dml.bulk_delete('name', 'cfr', 'verver/111')
        self.dml.bulk_put(layers, 'name', 'cfr')

        self.assertEqual(Layer.objects.count(), 2)
        self.assertEqual(self.dml.get('name', 'cfr', 'verver/111-23'),
                         {'111-23': [1]})


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
        self.dmn.delete('docdoc')
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

    def test_put_delete(self):
        """We can insert and replace a diff"""
        self.dmd.put('lablab', 'oldold', 'newnew', {"some": "structure"})

        expected = {"label": "lablab", "old_version": "oldold",
                    "new_version": "newnew", "diff": {"some": "structure"}}
        fields = expected.keys()
        six.assertCountEqual(self, Diff.objects.all().values(*fields),
                             [expected])

        self.dmd.delete('lablab', 'oldold', 'newnew')
        self.dmd.put('lablab', 'oldold', 'newnew', {"other": "structure"})
        expected['diff'] = {'other': 'structure'}
        six.assertCountEqual(self, Diff.objects.all().values(*fields),
                             [expected])
