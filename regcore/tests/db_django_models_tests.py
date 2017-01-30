import copy
from datetime import date

import pytest

from regcore.db.django_models import DMDiffs, DMDocuments, DMLayers, DMNotices
from regcore.models import Diff, Document, Layer, Notice


@pytest.mark.django_db
def test_get_404():
    assert DMDocuments().get('lablab', 'verver') is None


@pytest.mark.django_db
def test_doc_get_cfr():
    Document.objects.create(doc_type='cfr', version='verver',
                            label_string='a-b', text='ttt', node_type='tyty')
    assert DMDocuments().get('cfr', 'a-b', 'verver') == {
        'text': 'ttt',
        'label': ['a', 'b'],
        'lft': 1,
        'children': [],
        'node_type': 'tyty'
    }


@pytest.mark.django_db
def test_doc_get_preamble():
    Document.objects.create(doc_type='preamble', version='verver',
                            label_string='a-b', text='ttt', node_type='tyty')
    assert DMDocuments().get('preamble', 'a-b', 'verver') == {
        'text': 'ttt',
        'label': ['a', 'b'],
        'lft': 1,
        'children': [],
        'node_type': 'tyty'
    }


@pytest.mark.django_db
def test_doc_listing():
    dmr = DMDocuments()
    Document.objects.create(id='ver1-a-b', doc_type='cfr', version='ver1',
                            label_string='a-b', text='textex', node_type='ty')
    Document.objects.create(id='aaa-a-b', doc_type='cfr', version='aaa',
                            label_string='a-b', text='textex', node_type='ty')
    Document.objects.create(id='333-a-b', doc_type='cfr', version='333',
                            label_string='a-b', text='textex', node_type='ty')
    Document.objects.create(id='four-a-b', doc_type='cfr', version='four',
                            label_string='a-b', text='textex', node_type='ty')

    assert dmr.listing('cfr', 'a-b') == [
        ('333', 'a-b'), ('aaa', 'a-b'), ('four', 'a-b'), ('ver1', 'a-b')]

    Document.objects.create(id='ver1-1111', doc_type='cfr', version='ver1',
                            label_string='1111', text='aaaa', node_type='ty',
                            root=True)
    Document.objects.create(id='ver2-1111', doc_type='cfr', version='ver2',
                            label_string='1111', text='bbbb', node_type='ty',
                            root=True)
    Document.objects.create(id='ver3-1111', doc_type='cfr', version='ver3',
                            label_string='1111', text='cccc', node_type='ty',
                            root=False)

    assert dmr.listing('cfr') == [('ver1', '1111'), ('ver2', '1111')]


@pytest.mark.django_db
def test_doc_bulk_insert():
    """Writing multiple documents should save correctly. They can be
    modified. The lft and rght ids assigned by the Modified Preorder Tree
    Traversal algorithm are shown below:

                            (1)root(6)
                            /    \
                           /       \
                     (2)n2(3)    (4)n3(5)
    """
    dmr = DMDocuments()
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
    dmr.bulk_insert(nodes, 'cfr', 'verver')

    assert dmr.get('cfr', '111', 'verver') == original

    root['title'] = original['title'] = 'New Title'
    dmr.bulk_delete('cfr', '111', 'verver')
    dmr.bulk_insert(nodes, 'cfr', 'verver')

    assert dmr.get('cfr', '111', 'verver') == original


@pytest.mark.django_db
def test_layer_get_404():
    assert DMLayers().get('namnam', 'cfr', 'verver/lablab') is None


@pytest.mark.django_db
def test_layer_get_success():
    Layer.objects.create(name='namnam', doc_type='cfr', doc_id='verver/lablab',
                         layer={"some": "body"})
    assert DMLayers().get('namnam', 'cfr', 'verver/lablab') == {
        'some': 'body'}


@pytest.mark.django_db
def test_layer_bulk_insert():
    """Writing multiple documents should save correctly. They can be
    modified"""
    dml = DMLayers()
    layers = [{'111-22': [], '111-22-a': [], 'doc_id': 'verver/111-22'},
              {'111-23': [], 'doc_id': 'verver/111-23'}]
    dml.bulk_insert(layers, 'name', 'cfr')

    assert Layer.objects.count() == 2
    assert dml.get('name', 'cfr', 'verver/111-22') == {'111-22': [],
                                                       '111-22-a': []}
    assert dml.get('name', 'cfr', 'verver/111-23') == {'111-23': []}

    layers[1] = {'111-23': [1], 'doc_id': 'verver/111-23'}
    dml.bulk_delete('name', 'cfr', 'verver/111')
    dml.bulk_insert(layers, 'name', 'cfr')

    assert Layer.objects.count() == 2
    assert dml.get('name', 'cfr', 'verver/111-23') == {'111-23': [1]}


@pytest.mark.django_db
def test_notice_get_404():
    assert DMNotices().get('docdoc') is None


@pytest.mark.django_db
def test_notice_get_success():
    Notice.objects.create(document_number='docdoc', fr_url='frfr',
                          publication_date=date.today(),
                          notice={"some": "body"})
    assert DMNotices().get('docdoc') == {'some': 'body'}


@pytest.mark.django_db
def test_notice_listing():
    dmn = DMNotices()
    n = Notice.objects.create(document_number='22', fr_url='fr1', notice={},
                              effective_on=date(2005, 5, 5),
                              publication_date=date(2001, 3, 3))
    n.noticecfrpart_set.create(cfr_part='876')
    n = Notice.objects.create(document_number='9', fr_url='fr2', notice={},
                              publication_date=date(1999, 1, 1))
    n.noticecfrpart_set.create(cfr_part='876')
    n.noticecfrpart_set.create(cfr_part='111')

    assert dmn.listing() == [
        {'document_number': '22', 'fr_url': 'fr1',
         'publication_date': '2001-03-03', 'effective_on': '2005-05-05'},
        {'document_number': '9', 'fr_url': 'fr2',
         'publication_date': '1999-01-01'}
    ]

    assert dmn.listing() == dmn.listing('876')
    assert dmn.listing('888') == []


@pytest.mark.django_db
def test_notice_insert():
    """We can insert and replace a notice"""
    dmn = DMNotices()
    doc = {"some": "structure",
           'effective_on': '2011-01-01',
           'fr_url': 'http://example.com',
           'publication_date': '2010-02-02',
           'cfr_parts': ['222']}
    dmn.insert('docdoc', doc)

    expected = {"document_number": "docdoc",
                "effective_on": date(2011, 1, 1),
                "fr_url": "http://example.com",
                "publication_date": date(2010, 2, 2),
                "noticecfrpart__cfr_part": '222',
                "notice": doc}
    assert list(Notice.objects.all().values(*expected.keys())) == [expected]

    doc['fr_url'] = 'url2'
    dmn.delete('docdoc')
    dmn.insert('docdoc', doc)

    expected['fr_url'] = 'url2'
    assert list(Notice.objects.all().values(*expected.keys())) == [expected]


@pytest.mark.django_db
def test_diff_get_404():
    assert DMDiffs().get('lablab', 'oldold', 'newnew') is None


@pytest.mark.django_db
def test_diff_get_success():
    Diff.objects.create(label='lablab', old_version='oldold',
                        new_version='newnew', diff={"some": "body"})

    assert DMDiffs().get('lablab', 'oldold', 'newnew') == {'some': 'body'}


@pytest.mark.django_db
def test_diff_insert_delete():
    """We can insert and replace a diff"""
    dmd = DMDiffs()
    dmd.insert('lablab', 'oldold', 'newnew', {"some": "structure"})

    expected = {"label": "lablab", "old_version": "oldold",
                "new_version": "newnew", "diff": {"some": "structure"}}
    assert list(Diff.objects.all().values(*expected.keys())) == [expected]

    dmd.delete('lablab', 'oldold', 'newnew')
    dmd.insert('lablab', 'oldold', 'newnew', {"other": "structure"})
    expected['diff'] = {'other': 'structure'}
    assert list(Diff.objects.all().values(*expected.keys())) == [expected]
