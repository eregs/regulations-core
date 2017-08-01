"""If using the Elastic Search backend, this endpoint provides search
results. If using haystack, see haystack_search.py"""

from django.conf import settings
from pyelasticsearch import ElasticSearch
from webargs import ValidationError
from webargs.djangoparser import parser

from regcore.db.es import ESLayers
from regcore.responses import success, user_error
from regcore_read.views.search_utils import search_args

PAGE_SIZE = 50


def search(request, doc_type):
    """Search elastic search for any matches in the node's text"""
    try:
        args = parser.parse(search_args, request)
    except ValidationError as err:
        return user_error('. '.join(err.messages))

    term, version, regulation = args['q'], args['version'], args['regulation']
    is_root, is_subpart = args['is_root'], args['is_subpart']
    page = args['page']

    query = {
        'fields': ['text', 'label', 'version', 'regulation', 'title',
                   'label_string'],
        'from': page * PAGE_SIZE,
        'size': PAGE_SIZE,
    }
    text_match = {'match': {'text': term, 'doc_type': doc_type}}
    if version or regulation:
        term = {}
        if version:
            term['version'] = version
        if regulation:
            term['regulation'] = regulation
        if is_root is not None:
            term['is_root'] = is_root
        if is_subpart is not None:
            term['is_subpart'] = is_subpart
        query['query'] = {'filtered': {
            'query': text_match,
            'filter': {'term': term}
        }}
    else:
        query['query'] = text_match
    es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)
    results = es.search(query, index=settings.ELASTIC_SEARCH_INDEX)

    return success({
        'total_hits': results['hits']['total'],
        'results': transform_results([h['fields'] for h in
                                      results['hits']['hits']])
    })


def transform_results(results):
    """Pull out unused fields, add title field from layers if possible"""
    regulations = {(r['regulation'], r['version']) for r in results}

    layers = {}
    for regulation, version in regulations:
        terms = ESLayers().get('terms', regulation, version)
        # We need the references, not the locations of defined terms
        if terms:
            defined = {}
            for term_struct in terms['referenced'].values():
                defined[term_struct['reference']] = term_struct['term']
            terms = defined
        layers[(regulation, version)] = {
            'keyterms': ESLayers().get('keyterms', regulation, version),
            'terms': terms
        }

    for result in results:
        title = result.get('title', '')
        ident = (result['regulation'], result['version'])
        keyterms = layers[ident]['keyterms']
        terms = layers[ident]['terms']
        if not title and keyterms and result['label_string'] in keyterms:
            title = keyterms[result['label_string']][0]['key_term']
        if not title and terms and result['label_string'] in terms:
            title = terms[result['label_string']]

        if title:
            result['title'] = title

    return results
