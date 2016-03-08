from django.conf import settings
from django.utils.module_loading import import_string


def select_for(data_type):
    """The storage class for each datatype is defined in a settings file. This
    will look up the appropriate storage backend and instantiate it"""
    return import_string(settings.BACKENDS[data_type])()

for_regulations = select_for('regulations')
for_layers = select_for('layers')
for_notices = select_for('notices')
for_diffs = select_for('diffs')
