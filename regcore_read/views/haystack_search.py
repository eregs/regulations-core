"""If using the haystack backend, this endpoing provides search results. If
using Elastic Search, see es_search.py"""

from haystack.query import SearchQuerySet
from webargs import ValidationError
from webargs.djangoparser import parser

from regcore.db.django_models import DMLayers
from regcore.models import Document
from regcore.responses import success, user_error
from regcore_read.views.search_utils import search_args

PAGE_SIZE = 50


def search(request, doc_type):
    """Use haystack to find search results"""
    try:
        args = parser.parse(search_args, request)
    except ValidationError as err:
        return user_error('. '.join(err.messages))

    term, version, regulation = args['q'], args['version'], args['regulation']
    is_root, is_subpart = args['is_root'], args['is_subpart']
    page = args['page']

    query = SearchQuerySet().models(Document).filter(
        content=term, doc_type=doc_type)
    if version:
        query = query.filter(version=version)
    if regulation:
        query = query.filter(regulation=regulation)
    if is_root is not None:
        query = query.filter(is_root=is_root)
    if is_subpart is not None:
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
