from django.conf.urls import patterns

from regcore_read.views import diff as rdiff, layer as rlayer
from regcore_read.views import notice as rnotice, regulation as rregulation
from regcore_read.views import search
from regcore_write.views import diff as wdiff, layer as wlayer
from regcore_write.views import notice as wnotice, regulation as wregulation
from regcore.urls_utils import by_verb_url


# Re-usable URL patterns.
def seg(label):
    return r'(?P<%s>[-\d\w]+)' % label


urlpatterns = patterns(
    '',
    by_verb_url(r'^diff/%s/%s/%s$' % (seg('label_id'), seg('old_version'),
                                      seg('new_version')),
                'diff',
                GET=rdiff.get,
                PUT=wdiff.add),
    by_verb_url(r'^layer/%s/%s/%s$' % (seg('name'), seg('label_id'),
                                       seg('version')),
                'layer',
                GET=rlayer.get,
                PUT=wlayer.add),
    by_verb_url(r'^notice/%s$' % seg('docnum'),
                'notice',
                GET=rnotice.get,
                PUT=wnotice.add),
    by_verb_url(r'^notice$', 'notices', GET=rnotice.listing),
    by_verb_url(r'^regulation/%s$' % seg('label_id'),
                'reg-versions', GET=rregulation.listing),
    by_verb_url(r'^regulation/%s/%s$' % (seg('label_id'), seg('version')),
                'regulation',
                GET=rregulation.get,
                PUT=wregulation.add),
    by_verb_url(r'^search$', 'search', GET=search.search)
)
