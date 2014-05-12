# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NoticeCFRPart'
        db.create_table(u'regcore_noticecfrpart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cfr_part', self.gf('django.db.models.fields.SlugField')(max_length=10, db_index=True)),
            ('notice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['regcore.Notice'])),
        ))
        db.send_create_signal(u'regcore', ['NoticeCFRPart'])

        # Adding unique constraint on 'NoticeCFRPart', fields ['notice', 'cfr_part']
        db.create_unique(u'regcore_noticecfrpart', ['notice_id', 'cfr_part'])

        # Adding index on 'NoticeCFRPart', fields ['notice', 'cfr_part']
        db.create_index(u'regcore_noticecfrpart', ['notice_id', 'cfr_part'])


    def backwards(self, orm):
        # Removing index on 'NoticeCFRPart', fields ['notice', 'cfr_part']
        db.delete_index(u'regcore_noticecfrpart', ['notice_id', 'cfr_part'])

        # Removing unique constraint on 'NoticeCFRPart', fields ['notice', 'cfr_part']
        db.delete_unique(u'regcore_noticecfrpart', ['notice_id', 'cfr_part'])

        # Deleting model 'NoticeCFRPart'
        db.delete_table(u'regcore_noticecfrpart')


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
        u'regcore.noticecfrpart': {
            'Meta': {'unique_together': "(('notice', 'cfr_part'),)", 'object_name': 'NoticeCFRPart', 'index_together': "(('notice', 'cfr_part'),)"},
            'cfr_part': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['regcore.Notice']"})
        },
        u'regcore.regulation': {
            'Meta': {'unique_together': "(('version', 'label_string'),)", 'object_name': 'Regulation', 'index_together': "(('version', 'label_string'),)"},
            'children': ('regcore.fields.CompressedJSONField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_string': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'node_type': ('django.db.models.fields.SlugField', [], {'max_length': '10'}),
            'root': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['regcore']
