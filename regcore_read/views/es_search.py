"""If using the Elastic Search backend, this endpoint provides search
results. If using haystack, see haystack_search.py"""

from django.conf import settings
from pyelasticsearch import ElasticSearch

from regcore.db.es import ESLayers
from regcore.responses import success
from regcore_read.views.search_utils import requires_search_args


@requires_search_args
def search(request, doc_type, search_args):
    """Search elastic search for any matches in the node's text"""
    query = {
        'fields': ['text', 'label', 'version', 'regulation', 'title',
                   'label_string'],
        'from': search_args.page * search_args.page_size,
        'size': search_args.page_size,
    }
    text_match = {'match': {'text': search_args.q, 'doc_type': doc_type}}
    if search_args.version or search_args.regulation:
        term = {}
        if search_args.version:
            term['version'] = search_args.version
        if search_args.regulation:
            term['regulation'] = search_args.regulation
        if search_args.is_root is not None:
            term['is_root'] = search_args.is_root
        if search_args.is_subpart is not None:
            term['is_subpart'] = search_args.is_subpart
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
