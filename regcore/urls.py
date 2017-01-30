"""URLs file for Django. This will inspect the installed apps and only
include the read/write end points that are associated with the regcore_read
and regcore_write apps"""


from collections import defaultdict

from django.conf import settings

from regcore.urls_utils import by_verb_url
from regcore_read.views import diff as rdiff
from regcore_read.views import document as rdocument
from regcore_read.views import layer as rlayer
from regcore_read.views import notice as rnotice
from regcore_read.views.haystack_search import search
from regcore_write.views import diff as wdiff
from regcore_write.views import document as wdocument
from regcore_write.views import layer as wlayer
from regcore_write.views import notice as wnotice

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
    return r'(?P<{0}>[-\w]+)'.format(label)


urlpatterns = [
    by_verb_url(
        r'^diff/{0}/{1}/{2}$'.format(
            seg('label_id'), seg('old_version'), seg('new_version')),
        'diff', mapping['diff']),
    by_verb_url(
        r'^layer/{0}/{1}/{2}$'.format(
            seg('name'), seg('doc_type'), r'(?P<doc_id>[-\w]+(/[-\w]+)*)'),
        'layer', mapping['layer']),
    by_verb_url(r'^notice/{0}$'.format(seg('docnum')),
                'notice', mapping['notice']),
    by_verb_url(
        r'^regulation/{0}/{1}$'.format(seg('label_id'), seg('version')),
        'regulation', mapping['regulation'], kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^notice$', 'notices', mapping['notices']),
    by_verb_url(r'^regulation$', 'all-reg-versions', mapping['reg-versions'],
                kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^regulation/{0}$'.format(seg('label_id')),
                'reg-versions', mapping['reg-versions'],
                kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^preamble/{0}$'.format(seg('label_id')), 'preamble',
                mapping['preamble'], kwargs={'doc_type': 'preamble'}),
    by_verb_url(r'^search(?:/cfr)?$', 'search', mapping['search'],
                kwargs={'doc_type': 'cfr'}),
    by_verb_url(r'^search/preamble$', 'search', mapping['search'],
                kwargs={'doc_type': 'preamble'}),
]
