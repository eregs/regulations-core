from core import app
from core.responses import success
from elasticutils import Q, S
from flask import request
import settings

@app.route('/search')
def search():
    term = request.args.get('q', '')
    if not term:
        return user_error('No query term')

    search = S().es(urls=settings.ELASTIC_SEARCH_URLS)
    search = search.indexes(settings.ELASTIC_SEARCH_INDEX)
    #search = search.query(**{'label.title__text': term})
    search = search.query(text__text=term)

    return success([result.__dict__ for result in search.all()])
