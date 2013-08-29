# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Regulation'
        db.create_table(u'regcore_regulation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.SlugField')(max_length=20)),
            ('label_string', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('node_type', self.gf('django.db.models.fields.SlugField')(max_length=10)),
            ('children', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'regcore', ['Regulation'])

        # Adding unique constraint on 'Regulation', fields ['version', 'label_string']
        db.create_unique(u'regcore_regulation', ['version', 'label_string'])

        # Adding index on 'Regulation', fields ['version', 'label_string']
        db.create_index(u'regcore_regulation', ['version', 'label_string'])

        # Adding model 'Layer'
        db.create_table(u'regcore_layer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.SlugField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=20)),
            ('label', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('layer', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'regcore', ['Layer'])

        # Adding unique constraint on 'Layer', fields ['version', 'name', 'label']
        db.create_unique(u'regcore_layer', ['version', 'name', 'label'])

        # Adding index on 'Layer', fields ['version', 'name', 'label']
        db.create_index(u'regcore_layer', ['version', 'name', 'label'])

        # Adding model 'Notice'
        db.create_table(u'regcore_notice', (
            ('document_number', self.gf('django.db.models.fields.SlugField')(max_length=20, primary_key=True)),
            ('effective_on', self.gf('django.db.models.fields.DateField')(null=True)),
            ('fr_url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('publication_date', self.gf('django.db.models.fields.DateField')()),
            ('notice', self.gf('django.db.models.fields.TextField')()),
            ('cfr_part', self.gf('django.db.models.fields.SlugField')(max_length=10)),
        ))
        db.send_create_signal(u'regcore', ['Notice'])

        # Adding model 'Diff'
        db.create_table(u'regcore_diff', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('old_version', self.gf('django.db.models.fields.SlugField')(max_length=20)),
            ('new_version', self.gf('django.db.models.fields.SlugField')(max_length=20)),
            ('diff', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'regcore', ['Diff'])

        # Adding unique constraint on 'Diff', fields ['label', 'old_version', 'new_version']
        db.create_unique(u'regcore_diff', ['label', 'old_version', 'new_version'])

        # Adding index on 'Diff', fields ['label', 'old_version', 'new_version']
        db.create_index(u'regcore_diff', ['label', 'old_version', 'new_version'])


    def backwards(self, orm):
        # Removing index on 'Diff', fields ['label', 'old_version', 'new_version']
        db.delete_index(u'regcore_diff', ['label', 'old_version', 'new_version'])

        # Removing unique constraint on 'Diff', fields ['label', 'old_version', 'new_version']
        db.delete_unique(u'regcore_diff', ['label', 'old_version', 'new_version'])

        # Removing index on 'Layer', fields ['version', 'name', 'label']
        db.delete_index(u'regcore_layer', ['version', 'name', 'label'])

        # Removing unique constraint on 'Layer', fields ['version', 'name', 'label']
        db.delete_unique(u'regcore_layer', ['version', 'name', 'label'])

        # Removing index on 'Regulation', fields ['version', 'label_string']
        db.delete_index(u'regcore_regulation', ['version', 'label_string'])

        # Removing unique constraint on 'Regulation', fields ['version', 'label_string']
        db.delete_unique(u'regcore_regulation', ['version', 'label_string'])

        # Deleting model 'Regulation'
        db.delete_table(u'regcore_regulation')

        # Deleting model 'Layer'
        db.delete_table(u'regcore_layer')

        # Deleting model 'Notice'
        db.delete_table(u'regcore_notice')

        # Deleting model 'Diff'
        db.delete_table(u'regcore_diff')


    models = {
        u'regcore.diff': {
            'Meta': {'unique_together': "(('label', 'old_version', 'new_version'),)", 'object_name': 'Diff', 'index_together': "(('label', 'old_version', 'new_version'),)"},
            'diff': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'new_version': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            'old_version': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        },
        u'regcore.layer': {
            'Meta': {'unique_together': "(('version', 'name', 'label'),)", 'object_name': 'Layer', 'index_together': "(('version', 'name', 'label'),)"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'layer': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            'version': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        },
        u'regcore.notice': {
            'Meta': {'object_name': 'Notice'},
            'cfr_part': ('django.db.models.fields.SlugField', [], {'max_length': '10'}),
            'document_number': ('django.db.models.fields.SlugField', [], {'max_length': '20', 'primary_key': 'True'}),
            'effective_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fr_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notice': ('django.db.models.fields.TextField', [], {}),
            'publication_date': ('django.db.models.fields.DateField', [], {})
        },
        u'regcore.regulation': {
            'Meta': {'unique_together': "(('version', 'label_string'),)", 'object_name': 'Regulation', 'index_together': "(('version', 'label_string'),)"},
            'children': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_string': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'node_type': ('django.db.models.fields.SlugField', [], {'max_length': '10'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['regcore']