"""If using the haystack backend, this endpoing provides search results. If
using Elastic Search, see es_search.py"""

from haystack.query import SearchQuerySet

from regcore.db.django_models import DMLayers
from regcore.models import Document
from regcore.responses import success, user_error

PAGE_SIZE = 50


def validate_boolean(value):
    return value is None or value in ['true', 'false']


def search(request, doc_type):
    """Use haystack to find search results"""
    term = request.GET.get('q', '')
    version = request.GET.get('version', '')
    regulation = request.GET.get('regulation', '')
    is_root = request.GET.get('is_root')
    is_subpart = request.GET.get('is_subpart')
    try:
        page = int(request.GET.get('page', '0'))
    except ValueError:
        page = 0

    if not term:
        return user_error('No query term')
    if not validate_boolean(is_root):
        return user_error('Parameter "is_root" must be "true" or "false"')
    if not validate_boolean(is_subpart):
        return user_error('Parameter "is_subpart" must be "true" or "false"')

    query = SearchQuerySet().models(Document).filter(
        content=term, doc_type=doc_type)
    if version:
        query = query.filter(version=version)
    if regulation:
        query = query.filter(regulation=regulation)
    if is_root:
        query = query.filter(is_root=is_root)
    if is_subpart:
        query = query.filter(is_subpart=is_subpart)

    start, end = page * PAGE_SIZE, (page + 1) * PAGE_SIZE

    return success({
        'total_hits': len(query),
        'results': transform_results(query[start:end]),
    })


def transform_results(results):
    """Add title field from layers if possible"""
    regulations = {(r.regulation, r.version) for r in results}

    layers = {}
    for regulation, version in regulations:
        terms = DMLayers().get('terms', regulation, version)
        # We need the references, not the locations of defined terms
        if terms:
            defined = {}
            for term_struct in terms['referenced'].values():
                defined[term_struct['reference']] = term_struct['term']
            terms = defined
        layers[(regulation, version)] = {
            'keyterms': DMLayers().get('keyterms', regulation, version),
            'terms': terms
        }

    final_results = []
    for result in results:
        transformed = {
            'text': result.text,
            'label': result.label_string.split('-'),
            'version': result.version,
            'regulation': result.regulation,
            'label_string': result.label_string
        }

        if result.title:
            title = result.title[0]
        else:
            title = None
        ident = (result.regulation, result.version)
        keyterms = layers[ident]['keyterms']
        terms = layers[ident]['terms']
        if not title and keyterms and result.label_string in keyterms:
            title = keyterms[result.label_string][0]['key_term']
        if not title and terms and result.label_string in terms:
            title = terms[result.label_string]

        if title:
            transformed['title'] = title

        final_results.append(transformed)

    return final_results
