from regcore.responses import success, user_error
from flask import Blueprint, request
from pyelasticsearch import ElasticSearch
import settings

blueprint = Blueprint('search', __name__)

@blueprint.route('/search')
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

    return success({'results': results['hits']['hits']})
