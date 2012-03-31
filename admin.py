# -*- coding: utf-8 -*-
"""
Model admin
"""
from django.contrib import admin
from models import *

class MessageAdmin(admin.ModelAdmin):
    list_display = ('created', 'author', 'user_agent', 'clock', 'raw', 'ip')
    list_filter = ('created','author')
    ordering = ('-created',)

class FilterEntryAdmin(admin.ModelAdmin):
    list_display = ('author', 'target', 'kind', 'value')
    list_filter = ('target', 'kind')
    ordering = ('author', 'target', 'kind')

admin.site.register(UserPreferences)
admin.site.register(FilterEntry, FilterEntryAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Url)
