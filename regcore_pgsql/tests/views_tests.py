import pytest
from django.db.models import Q
from mock import call, Mock

pytest.importorskip('django', minversion='1.10')    # noqa
from regcore.tests.recipes import doc_recipe
from regcore_pgsql import views
from regcore_read.views.search_utils import SearchArgs


def make_queryset_mock():
    """Mocked queryset which returns itself for most manipulations."""
    queryset_mock = Mock()
    for transform in ('annotate', 'filter', 'order_by'):
        getattr(queryset_mock, transform).return_value = queryset_mock
    return queryset_mock


def test_matching_sections(monkeypatch):
    """Search arguments should be converted to the correct arguments."""
    queryset_mock = make_queryset_mock()
    monkeypatch.setattr(views.Document, 'objects', queryset_mock)

    result = views.matching_sections(SearchArgs(
        q='some terms', version='vvv', regulation='rrr',
        is_root=None, is_subpart=None, page=0, page_size=10))
    assert result == queryset_mock
    # no point in repeating the exact calls here; test the general flow
    assert 'some terms' in str(queryset_mock.annotate.call_args)
    assert 'search_vector' in str(queryset_mock.annotate.call_args)
    filters = queryset_mock.filter.call_args_list
    assert call(version='vvv') in filters
    assert call(documentindex__doc_root='rrr') in filters


@pytest.mark.django_db
def test_transform_results(monkeypatch):
    """If there's a text match inside a section, we should convert it to a
    dictionary."""
    monkeypatch.setattr(    # __search isn't supported by sqlite
        views, 'Q', Mock(return_value=Q(text__contains='matching')))
    sect = doc_recipe.make(label_string='root-11', title='Sect 111',
                           version='vvv')
    par_a = doc_recipe.make(label_string='root-11-a', parent=sect)
    doc_recipe.make(text='matching text', label_string='root-11-a-3',
                    parent=par_a, title="Match's title")

    results = views.transform_results([sect], 'this is a query')
    assert results == [{
        'text': 'matching text',
        'label': ['root', '11', 'a', '3'],
        'version': 'vvv',
        'regulation': 'root',
        'label_string': 'root-11-a-3',
        'match_title': "Match's title",
        'paragraph_title': "Match's title",
        'section_title': 'Sect 111',
        'title': 'Sect 111',
    }]


@pytest.mark.django_db
def test_transform_title_match(monkeypatch):
    """If there's a title match with no text, we should conver to the correct
    dictionary."""
    monkeypatch.setattr(    # __search isn't supported by sqlite
        views, 'Q', Mock(return_value=Q(title__contains='matching')))
    sect = doc_recipe.make(label_string='root-11', title='Sect 111',
                           version='vvv')
    par_a = doc_recipe.make(label_string='root-11-a', parent=sect, text='',
                            title='matching title')
    doc_recipe.make(label_string='root-11-a-3', parent=par_a,
                    text='inner text', title='inner title')

    results = views.transform_results([sect], 'this is a query')
    assert results == [{
        'text': 'inner text',
        'label': ['root', '11', 'a'],
        'version': 'vvv',
        'regulation': 'root',
        'label_string': 'root-11-a',
        'match_title': 'matching title',
        'paragraph_title': 'inner title',
        'section_title': 'Sect 111',
        'title': 'Sect 111',
    }]


@pytest.mark.django_db
def test_transform_no_exact_match(monkeypatch):
    """If text is searched text is broken across multiple paragraphs, we
    should just graph the first text node we can find."""
    monkeypatch.setattr(    # __search isn't supported by sqlite
        views, 'Q', Mock(return_value=Q(text=None)))    # will have no results
    sect = doc_recipe.make(label_string='root-11', text='', title='Sect 111',
                           version='vvv')
    par_a = doc_recipe.make(label_string='root-11-a', parent=sect,
                            text='has some text', title='nonmatching title')
    doc_recipe.make(label_string='root-11-a-3', parent=par_a)

    results = views.transform_results([sect], 'this is a query')
    assert results == [{
        'text': 'has some text',
        'label': ['root', '11'],
        'version': 'vvv',
        'regulation': 'root',
        'label_string': 'root-11',
        'match_title': 'Sect 111',
        'paragraph_title': 'nonmatching title',
        'section_title': 'Sect 111',
        'title': 'Sect 111',
    }]
