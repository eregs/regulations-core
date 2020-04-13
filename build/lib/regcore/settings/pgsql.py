from regcore.settings.base import *     # noqa

INSTALLED_APPS.remove('haystack')
INSTALLED_APPS.extend(['regcore_pgsql', 'django.contrib.postgres'])
SEARCH_HANDLER = 'regcore_pgsql.views.search'
