from django.conf.urls import patterns

from regcore.views import diff#, layer, notice, regulation, search
from regcore.urls_utils import by_verb_url


#Re-usable URL patterns. 
def seg(label):
    return r'(?P<%s>[-\d\w]+)' % label


urlpatterns = patterns('',
    by_verb_url(r'^diff/%s/%s/%s$' % (seg('label_id'), seg('old_version'),
                                       seg('new_version')),
                'diff',
                GET=diff.get,
                PUT=diff.add),
)
"""
by_verb_url(r'^/layer/%s/%s/%s$' % (r'(?<name>[^/]+)', label_id,
                                  version()),
            'layer',
            GET=layer.get,
            PUT=layer.add),
by_verb_url(r'^/notice/%s$' % version('docnum'),
            'notice',
            GET=notice.get,
            PUT=notice.add),
by_verb_url(r'^/notice$', 'notices', GET=notice.listing),
by_verb_url(r'^/regulation/%s$' % label_id,
            'reg-versions', GET=regulation.listing),
by_verb_url(r'^/regulation/%s/%s$' % (label_id, version()),
            'regulation',
            GET=regulation.get,
            PUT=regulation.add),
by_verb_url(r'^/search$', 'search', GET=search.search)
"""
