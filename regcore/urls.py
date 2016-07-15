"""URLs file for Django. This will inspect the installed apps and only
include the read/write end points that are associated with the regcore_read
and regcore_write apps"""


from collections import defaultdict

from django.conf import settings

from regcore_read.views import (
    diff as rdiff, layer as rlayer, notice as rnotice,
    document as rdocument)
from regcore_read.views.haystack_search import search
from regcore_write.views import (
    diff as wdiff, layer as wlayer, notice as wnotice,
    document as wdocument)
from regcore.urls_utils import by_verb_url


mapping = defaultdict(dict)


if 'regcore_read' in settings.INSTALLED_APPS:
    mapping['diff']['GET'] = rdiff.get
    mapping['layer']['GET'] = rlayer.get
    mapping['notice']['GET'] = rnotice.get
    mapping['notices']['GET'] = rnotice.listing
    mapping['preamble']['GET'] = rdocument.get
    mapping['regulation']['GET'] = rdocument.get
    mapping['reg-versions']['GET'] = rdocument.listing
    mapping['search']['GET'] = search


if 'regcore_write' in settings.INSTALLED_APPS:
    # Allow both PUT and POST
    for verb in ('PUT', 'POST'):
        mapping['diff'][verb] = wdiff.add
        mapping['layer'][verb] = wlayer.add
        mapping['notice'][verb] = wnotice.add
        mapping['preamble'][verb] = wdocument.add
        mapping['regulation'][verb] = wdocument.add
    mapping['diff']['DELETE'] = wdiff.delete
    mapping['layer']['DELETE'] = wlayer.delete
    mapping['notice']['DELETE'] = wnotice.delete
    mapping['preamble']['DELETE'] = wdocument.delete
    mapping['regulation']['DELETE'] = wdocument.delete


# Re-usable URL patterns.
def seg(label):
    return r'(?P<%s>[-\w]+)' % label


urlpatterns = [
    by_verb_url(r'^diff/%s/%s/%s$' % (seg('label_id'), seg('old_version'),
                                      seg('new_version')),
                'diff', mapping['diff']),
    by_verb_url(r'^layer/{}/{}/{}$'.format(
        seg('name'), seg('doc_type'), r'(?P<doc_id>[-\w]+(/[-\w]+)*)'),
        'layer', mapping['layer']),
    by_verb_url(r'^notice/%s$' % seg('docnum'),
                'notice', mapping['notice']),
    by_verb_url(r'^regulation/%s/%s$' % (seg('label_id'), seg('version')),
                'regulation', mapping['regulation'],
                kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^notice$', 'notices', mapping['notices']),
    by_verb_url(r'^regulation$', 'all-reg-versions', mapping['reg-versions'],
                kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^regulation/%s$' % seg('label_id'),
                'reg-versions', mapping['reg-versions'],
                kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^preamble/%s$' % seg('label_id'), 'preamble',
                mapping['preamble'], kwargs={'doc_type': 'preamble'}),
    by_verb_url(r'^search(?:/cfr)?$', 'search', mapping['search'],
                kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^search/preamble$', 'search', mapping['search'],
                kwargs={'doc_type': 'preamble'}),
]
