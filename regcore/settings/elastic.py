from regcore.settings.base import *     # noqa

INSTALLED_APPS.remove('haystack')
BACKENDS = {
    'regulations': 'regcore.db.es.ESRegulations',
    'layers': 'regcore.db.es.ESLayers',
    'notices': 'regcore.db.es.ESNotices',
    'diffs': 'regcore.db.es.ESDiffs'
}
SEARCH_HANDLER = 'regcore_read.views.es_search.search'
