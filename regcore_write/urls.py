from django.conf.urls import patterns

from regcore_write.views import diff, layer, notice, regulation
from regcore.urls_utils import by_verb_url


# Re-usable URL patterns.
def seg(label):
    return r'(?P<%s>[-\d\w]+)' % label


urlpatterns = patterns(
    '',
    by_verb_url(r'^diff/%s/%s/%s$' % (seg('label_id'), seg('old_version'),
                                      seg('new_version')),
                'diff',
                PUT=diff.add),
    by_verb_url(r'^layer/%s/%s/%s$' % (seg('name'), seg('label_id'),
                                       seg('version')),
                'layer',
                PUT=layer.add),
    by_verb_url(r'^notice/%s$' % seg('docnum'),
                'notice',
                PUT=notice.add),
    by_verb_url(r'^regulation/%s/%s$' % (seg('label_id'), seg('version')),
                'regulation',
                PUT=regulation.add)
)
