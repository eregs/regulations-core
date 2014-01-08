"""If using the Elastic Search backend, this endpoint provides search
results. If using haystack, see haystack_search.py"""

from django.conf import settings
from pyelasticsearch import ElasticSearch

from regcore import db
from regcore.responses import success, user_error


PAGE_SIZE = 50


def search(request):
    """Search elastic search for any matches in the node's text"""
    term = request.GET.get('q', '')
    version = request.GET.get('version', '')
    regulation = request.GET.get('regulation', '')
    try:
        page = int(request.GET.get('page', '0'))
    except ValueError:
        page = 0

    if not term:
        return user_error('No query term')

    query = {
        'fields': ['text', 'label', 'version', 'regulation', 'title',
                   'label_string'],
        'from': page*PAGE_SIZE,
        'size': PAGE_SIZE,
    }
    text_match = {'match': {'text': term}}
    if version or regulation:
        term = {}
        if version:
            term['version'] = version
        if regulation:
            term['regulation'] = regulation
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
    regulations = set((r['regulation'], r['version']) for r in results)

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
