from core import app
from core.responses import success, user_error
from flask import request
from pyelasticsearch import ElasticSearch
import settings

@app.route('/search')
def search():
    """Search elastic search for any matches in the node's text"""
    term = request.args.get('q', '')
    if not term:
        return user_error('No query term')

    query = {
        'fields': ['text', 'label', 'version'],
        'query': {'match': {'text': term}}
    }
    es = ElasticSearch(settings.ELASTIC_SEARCH_URLS)
    results = es.search(query, index=settings.ELASTIC_SEARCH_INDEX)

    return success(results['hits']['hits'])
