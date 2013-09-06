from django.conf import settings
from pyelasticsearch import ElasticSearch

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
        'fields': ['text', 'label', 'version'],
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
        'results': map(lambda h: h['fields'], results['hits']['hits'])
    })
