# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='regulation',
            name='children',
        ),
        migrations.AddField(
            model_name='regulation',
            name='level',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regulation',
            name='lft',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regulation',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='regcore.Regulation', null=True),
        ),
        migrations.AddField(
            model_name='regulation',
            name='rght',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regulation',
            name='tree_id',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='regulation',
            name='id',
            field=models.TextField(serialize=False, primary_key=True),
        ),
    ]
