from importlib import import_module

from django.conf import settings


def select_for(data_type):
    """The storage class for each datatype is defined in a settings file. This
    will look up the appropriate storage backend and instantiate it"""
    module, class_name = settings.BACKENDS[data_type].rsplit('.', 1)
    module = import_module(module)
    return getattr(module, class_name)()

for_regulations = select_for('regulations')
for_layers = select_for('layers')
for_notices = select_for('notices')
for_diffs = select_for('diffs')
