from django.conf.urls import patterns

from regcore_read.views import diff, layer, notice, regulation, search
from regcore.urls_utils import by_verb_url


# Re-usable URL patterns.
def seg(label):
    return r'(?P<%s>[-\d\w]+)' % label


urlpatterns = patterns(
    '',
    by_verb_url(r'^diff/%s/%s/%s$' % (seg('label_id'), seg('old_version'),
                                      seg('new_version')),
                'diff',
                GET=diff.get),
    by_verb_url(r'^layer/%s/%s/%s$' % (seg('name'), seg('label_id'),
                                       seg('version')),
                'layer',
                GET=layer.get),
    by_verb_url(r'^notice/%s$' % seg('docnum'),
                'notice',
                GET=notice.get),
    by_verb_url(r'^notice$', 'notices', GET=notice.listing),
    by_verb_url(r'^regulation/%s$' % seg('label_id'),
                'reg-versions', GET=regulation.listing),
    by_verb_url(r'^regulation/%s/%s$' % (seg('label_id'), seg('version')),
                'regulation',
                GET=regulation.get),
    by_verb_url(r'^search$', 'search', GET=search.search)
)
