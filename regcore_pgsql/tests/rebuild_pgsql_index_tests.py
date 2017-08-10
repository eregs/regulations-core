import pytest
from django.core.management import call_command
from mock import Mock

pytest.importorskip('django', minversion='1.10')    # noqa
from regcore.tests.recipes import doc_recipe
from regcore_pgsql.management.commands import rebuild_pgsql_index
from regcore_pgsql.models import DocumentIndex


@pytest.mark.django_db
def test_section_documents():
    """Should only grab sections, not the root or paragraphs"""
    root = doc_recipe.make(label_string='root')
    section1 = doc_recipe.make(label_string='root-1', parent=root)
    p1a = doc_recipe.make(label_string='root-1-a', parent=section1)
    doc_recipe.make(label_string='root-1-a-1', parent=p1a)
    doc_recipe.make(label_string='root-1-b', parent=section1)
    doc_recipe.make(label_string='root-2', parent=root)

    results = rebuild_pgsql_index.section_documents()

    assert {d.label_string for d in results} == {'root-1', 'root-2'}


@pytest.mark.django_db
def test_creates_index(monkeypatch):
    """We should see a new DocumentIndex per section, containing the text of
    all children"""
    monkeypatch.setattr(rebuild_pgsql_index.DocumentIndex,
                        'rebuild_search_vectors', Mock())
    root = doc_recipe.make(label_string='root')
    section1 = doc_recipe.make(label_string='root-1', parent=root)
    p1a = doc_recipe.make(label_string='root-1-a', parent=section1)
    p1a1 = doc_recipe.make(label_string='root-1-a-1', parent=p1a)
    p1b = doc_recipe.make(label_string='root-1-b', parent=section1)
    section2 = doc_recipe.make(label_string='root-2', parent=root)
    p2c = doc_recipe.make(label_string='root-2-c', parent=section2)

    call_command('rebuild_pgsql_index')
    rebuild_fn = rebuild_pgsql_index.DocumentIndex.rebuild_search_vectors
    assert rebuild_fn.call_count == 1

    indexes = DocumentIndex.objects.order_by('document__label_string')
    assert indexes.count() == 2
    index1, index2 = indexes

    for d in (root, section2, p2c):
        assert d.text not in index1.combined_text
        assert d.title not in index1.combined_titles
    for d in (section1, p1a, p1a1, p1b):
        assert d.text in index1.combined_text
        assert d.title in index1.combined_titles
    assert section1.title == index1.root_title

    for d in (root, section1, p1a, p1a1, p1b):
        assert d.text not in index2.combined_text
        assert d.title not in index2.combined_titles
    for d in (section2, p2c):
        assert d.text in index2.combined_text
        assert d.title in index2.combined_titles
    assert section2.title == index2.root_title
