# -*- coding: utf-8 -*-
# flake8: noqa
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cluster'
        db.create_table('documents_cluster', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('parameters', self.gf('django.db.models.fields.TextField')(default={})),
        ))
        db.send_create_signal('documents', ['Cluster'])

        # Adding M2M table for field documents on 'Cluster'
        db.create_table('documents_cluster_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cluster', models.ForeignKey(orm['documents.cluster'], null=False)),
            ('document', models.ForeignKey(orm['documents.document'], null=False))
        ))
        db.create_unique('documents_cluster_documents', ['cluster_id', 'document_id'])


    def backwards(self, orm):
        # Deleting model 'Cluster'
        db.delete_table('documents_cluster')

        # Removing M2M table for field documents on 'Cluster'
        db.delete_table('documents_cluster_documents')


    models = {
        'documents.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['documents.Document']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.TextField', [], {'default': '{}'})
        },
        'documents.document': {
            'Meta': {'object_name': 'Document'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['documents']
