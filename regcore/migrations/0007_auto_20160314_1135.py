# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def gen_layer_reference(apps, schema_editor):
    """We'll combine two previously distinct fields to generalize the layers
    interface"""
    Layer = apps.get_model("regcore", "Layer")
    for layer in Layer.objects.iterator():
        layer.reference = "{}:{}".format(layer.version, layer.label)
        layer.save()


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0006_auto_20160314_1126'),
    ]

    operations = [
        migrations.RunPython(gen_layer_reference)
    ]
