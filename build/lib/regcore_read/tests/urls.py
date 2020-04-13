from django.conf.urls import url

from regcore_read.views import es_search, haystack_search

urlpatterns = [
    url(r'^es_search$', es_search.search, kwargs={'doc_type': 'cfr'}),
    url(
        r'^haystack_search$',
        haystack_search.search,
        kwargs={'doc_type': 'cfr'},
    ),
]
