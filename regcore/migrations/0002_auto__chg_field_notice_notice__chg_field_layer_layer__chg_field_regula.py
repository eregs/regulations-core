# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Notice.notice'
        db.alter_column(u'regcore_notice', 'notice', self.gf('regcore.fields.CompressedJSONField')())

        # Changing field 'Layer.layer'
        db.alter_column(u'regcore_layer', 'layer', self.gf('regcore.fields.CompressedJSONField')())

        # Changing field 'Regulation.children'
        db.alter_column(u'regcore_regulation', 'children', self.gf('regcore.fields.CompressedJSONField')())

        # Changing field 'Diff.diff'
        db.alter_column(u'regcore_diff', 'diff', self.gf('regcore.fields.CompressedJSONField')())

    def backwards(self, orm):

        # Changing field 'Notice.notice'
        db.alter_column(u'regcore_notice', 'notice', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Layer.layer'
        db.alter_column(u'regcore_layer', 'layer', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Regulation.children'
        db.alter_column(u'regcore_regulation', 'children', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Diff.diff'
        db.alter_column(u'regcore_diff', 'diff', self.gf('django.db.models.fields.TextField')())

    models = {
        u'regcore.diff': {
            'Meta': {'unique_together': "(('label', 'old_version', 'new_version'),)", 'object_name': 'Diff', 'index_together': "(('label', 'old_version', 'new_version'),)"},
            'diff': ('regcore.fields.CompressedJSONField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'new_version': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            'old_version': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        },
        u'regcore.layer': {
            'Meta': {'unique_together': "(('version', 'name', 'label'),)", 'object_name': 'Layer', 'index_together': "(('version', 'name', 'label'),)"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'layer': ('regcore.fields.CompressedJSONField', [], {}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            'version': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        },
        u'regcore.notice': {
            'Meta': {'object_name': 'Notice'},
            'cfr_part': ('django.db.models.fields.SlugField', [], {'max_length': '10'}),
            'document_number': ('django.db.models.fields.SlugField', [], {'max_length': '20', 'primary_key': 'True'}),
            'effective_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fr_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notice': ('regcore.fields.CompressedJSONField', [], {}),
            'publication_date': ('django.db.models.fields.DateField', [], {})
        },
        u'regcore.regulation': {
            'Meta': {'unique_together': "(('version', 'label_string'),)", 'object_name': 'Regulation', 'index_together': "(('version', 'label_string'),)"},
            'children': ('regcore.fields.CompressedJSONField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_string': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'node_type': ('django.db.models.fields.SlugField', [], {'max_length': '10'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['regcore']
