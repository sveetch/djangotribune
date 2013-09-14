# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Channel'
        db.create_table('djangotribune_channel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=75)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=55)),
        ))
        db.send_create_signal('djangotribune', ['Channel'])

        # Adding model 'UserPreferences'
        db.create_table('djangotribune_userpreferences', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('refresh_time', self.gf('django.db.models.fields.IntegerField')(default=5000)),
            ('refresh_actived', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('smileys_host_url', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('maximised', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('djangotribune', ['UserPreferences'])

        # Adding model 'FilterEntry'
        db.create_table('djangotribune_filterentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('djangotribune', ['FilterEntry'])

        # Adding model 'Message'
        db.create_table('djangotribune_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['djangotribune.Channel'], null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('clock', self.gf('django.db.models.fields.TimeField')(auto_now_add=True, blank=True)),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('raw', self.gf('django.db.models.fields.TextField')()),
            ('web_render', self.gf('django.db.models.fields.TextField')()),
            ('remote_render', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djangotribune', ['Message'])

        # Adding model 'Url'
        db.create_table('djangotribune_url', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangotribune.Message'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('url', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djangotribune', ['Url'])


    def backwards(self, orm):
        # Deleting model 'Channel'
        db.delete_table('djangotribune_channel')

        # Deleting model 'UserPreferences'
        db.delete_table('djangotribune_userpreferences')

        # Deleting model 'FilterEntry'
        db.delete_table('djangotribune_filterentry')

        # Deleting model 'Message'
        db.delete_table('djangotribune_message')

        # Deleting model 'Url'
        db.delete_table('djangotribune_url')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangotribune.channel': {
            'Meta': {'object_name': 'Channel'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '75'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '55'})
        },
        'djangotribune.filterentry': {
            'Meta': {'object_name': 'FilterEntry'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'djangotribune.message': {
            'Meta': {'object_name': 'Message'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['djangotribune.Channel']", 'null': 'True', 'blank': 'True'}),
            'clock': ('django.db.models.fields.TimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'raw': ('django.db.models.fields.TextField', [], {}),
            'remote_render': ('django.db.models.fields.TextField', [], {}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'web_render': ('django.db.models.fields.TextField', [], {})
        },
        'djangotribune.url': {
            'Meta': {'object_name': 'Url'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangotribune.Message']"}),
            'url': ('django.db.models.fields.TextField', [], {})
        },
        'djangotribune.userpreferences': {
            'Meta': {'object_name': 'UserPreferences'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximised': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'refresh_actived': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'refresh_time': ('django.db.models.fields.IntegerField', [], {'default': '5000'}),
            'smileys_host_url': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        }
    }

    complete_apps = ['djangotribune']