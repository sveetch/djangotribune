# -*- coding: utf-8 -*-
"""
Model admin
"""
from django.contrib import admin
from models import *

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'created')
    ordering = ('-created',)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('channel', 'get_created_date', 'clock', 'get_identity', 'raw', 'ip')
    list_display_links = ('get_created_date', 'clock')
    list_filter = ('created', 'channel')
    search_fields = ['raw','author__username', 'user_agent','ip']
    ordering = ('-created',)

class FilterEntryAdmin(admin.ModelAdmin):
    list_display = ('author', 'target', 'kind', 'value')
    list_filter = ('target', 'kind')
    ordering = ('author', 'target', 'kind')

class UrlAdmin(admin.ModelAdmin):
    list_display = ('url', 'created')
    list_filter = ('created',)
    raw_id_fields = ("message",)

class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('owner', 'created')
    list_filter = ('created',)

admin.site.register(Channel, ChannelAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(FilterEntry, FilterEntryAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Url, UrlAdmin)
