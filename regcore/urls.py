"""URLs file for Django. This will inspect the installed apps and only
include the read/write end points that are associated with the regcore_read
and regcore_write apps"""


from collections import defaultdict

from django.conf import settings
from django.conf.urls import patterns

from regcore_read.views import (
    diff as rdiff, layer as rlayer, notice as rnotice,
    regulation as rregulation)
from regcore_read.views.haystack_search import search
from regcore_write.views import (
    diff as wdiff, layer as wlayer, notice as wnotice,
    regulation as wregulation)
from regcore.urls_utils import by_verb_url


mapping = defaultdict(dict)


if 'regcore_read' in settings.INSTALLED_APPS:
    mapping['diff']['GET'] = rdiff.get
    mapping['layer']['GET'] = rlayer.get
    mapping['notice']['GET'] = rnotice.get
    mapping['notices']['GET'] = rnotice.listing
    mapping['preamble']['GET'] = rregulation.get
    mapping['regulation']['GET'] = rregulation.get
    mapping['reg-versions']['GET'] = rregulation.listing
    mapping['search']['GET'] = search


if 'regcore_write' in settings.INSTALLED_APPS:
    # Allow both PUT and POST
    for verb in ('PUT', 'POST'):
        mapping['diff'][verb] = wdiff.add
        mapping['layer'][verb] = wlayer.add
        mapping['notice'][verb] = wnotice.add
        mapping['preamble'][verb] = wregulation.add
        mapping['regulation'][verb] = wregulation.add


# Re-usable URL patterns.
def seg(label):
    return r'(?P<%s>[-\w]+)' % label


urlpatterns = patterns(
    '',
    by_verb_url(r'^diff/%s/%s/%s$' % (seg('label_id'), seg('old_version'),
                                      seg('new_version')),
                'diff', mapping['diff']),
    by_verb_url(r'^layer/{}/{}/{}$'.format(
        seg('name'), seg('doc_type'), r'(?P<doc_id>[-\w]+(/[-\w]+)*)'),
        'layer', mapping['layer']),
    by_verb_url(r'^notice/%s$' % seg('docnum'),
                'notice', mapping['notice']),
    by_verb_url(r'^regulation/%s/%s$' % (seg('label_id'), seg('version')),
                'regulation', mapping['regulation']),
    by_verb_url(r'^notice$', 'notices', mapping['notices']),
    by_verb_url(r'^regulation$', 'all-reg-versions', mapping['reg-versions']),
    by_verb_url(r'^regulation/%s$' % seg('label_id'),
                'reg-versions', mapping['reg-versions'],
                kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^preamble/%s$' % seg('label_id'), 'preamble',
                mapping['preamble'], kwargs={'doc_type': 'preamble'}),
    by_verb_url(r'^search$', 'search', mapping['search'])
)
