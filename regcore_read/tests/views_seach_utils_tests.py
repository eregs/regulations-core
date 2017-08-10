import pytest

from regcore_read.views import search_utils


def inner_fn(request, search_args):
    # We'd generally return a Response here, but we're mocking
    return search_args


@pytest.mark.parametrize('page_size', ('-10', '0', '200', 'abcd', '---'))
def test_invalid_page_size(page_size, rf):
    """Invalid page sizes should not be admitted."""
    view = search_utils.requires_search_args(inner_fn)
    result = view(rf.get('?q=term&page_size={0}'.format(page_size)))
    assert result.status_code == 400


def test_valid_page_size(rf):
    """Valid page sizes should pass through."""
    view = search_utils.requires_search_args(inner_fn)
    result = view(rf.get('?q=term'))

    result = view(rf.get('?q=term&page_size=10'))
    assert result.page_size == 10
