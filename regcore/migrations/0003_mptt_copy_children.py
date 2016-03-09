# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from regcore_write.views.regulation import write_node


def rebuild(apps, schema_editor):
    Regulation = apps.get_model('regcore', 'Regulation')
    Regulation.objects.filter(root=False).delete()
    for root in Regulation.objects.all():
        serialized = {
            'text': root.text,
            'title': root.title,
            'label': root.label_string.split('-'),
            'node_type': root.node_type,
            'children': root.children,
        }
        root.delete()
        write_node(serialized, root.version, root.label_string)


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0002_mptt_add_fields'),
    ]

    operations = [
        migrations.RunPython(rebuild),
    ]
