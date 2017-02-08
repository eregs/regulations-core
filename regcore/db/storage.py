from django.conf import settings
from django.utils.module_loading import import_string


def select_for(data_type):
    """The storage class for each datatype is defined in a settings file. This
    will look up the appropriate storage backend and instantiate it. If none
    is found, this will default to the Django ORM versions"""
    class_str = settings.BACKENDS.get(
        data_type,
        'regcore.db.django_models.DM' + data_type.capitalize())
    return import_string(class_str)()


for_documents = select_for('documents')
for_layers = select_for('layers')
for_notices = select_for('notices')
for_diffs = select_for('diffs')
