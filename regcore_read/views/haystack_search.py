"""If using the haystack backend, this endpoing provides search results. If
using Elastic Search, see es_search.py"""

from haystack.query import SearchQuerySet

from regcore import db
from regcore.models import Regulation
from regcore.responses import success, user_error


PAGE_SIZE = 50


def search(request):
    """Use haystack to find search results"""
    term = request.GET.get('q', '')
    version = request.GET.get('version', '')
    regulation = request.GET.get('regulation', '')
    try:
        page = int(request.GET.get('page', '0'))
    except ValueError:
        page = 0

    if not term:
        return user_error('No query term')

    query = SearchQuerySet().models(Regulation).filter(content=term)
    if version:
        query = query.filter(version=version)
    if regulation:
        query = query.filter(regulation=regulation)

    start, end = page * PAGE_SIZE, (page+1) * PAGE_SIZE

    return success({
        'total_hits': len(query),
        'results': transform_results(query[start:end])
    })


def transform_results(results):
    """Add title field from layers if possible"""
    regulations = set((r.regulation, r.version) for r in results)

    layers = {}
    for regulation, version in regulations:
        terms = db.Layers().get('terms', regulation, version)
        # We need the references, not the locations of defined terms
        if terms:
            defined = {}
            for term_struct in terms['referenced'].values():
                defined[term_struct['reference']] = term_struct['term']
            terms = defined
        layers[(regulation, version)] = {
            'keyterms': db.Layers().get('keyterms', regulation, version),
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
