import pytest
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


def test_transform_results():
    """Verify conversion to a dict."""
    sect1, sect2 = Mock(title='Section 111'), Mock(title='Section 222')
    query1, query2 = make_queryset_mock(), make_queryset_mock()
    sect1.get_descendants.return_value = query1
    sect2.get_descendants.return_value = query2
    query1.first.return_value = doc_recipe.prepare(
        text='sect1', label_string='root-111', version='vvv',
        title='Section 111')
    query2.first.return_value = doc_recipe.prepare(
        text='subpar', label_string='root-222-a-3', version='vvv')

    assert views.transform_results([sect1, sect2], 'my terms') == [
        dict(text='sect1', label=['root', '111'], version='vvv',
             regulation='root', label_string='root-111', title='Section 111'),
        dict(text='subpar', label=['root', '222', 'a', '3'], version='vvv',
             regulation='root', label_string='root-222-a-3',
             title='Section 222'),
    ]
