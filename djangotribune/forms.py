# -*- coding: utf-8 -*-
"""
Forms
"""
import copy, datetime, operator, pytz

from django.conf import settings
from django import forms
from django.utils.html import escape as html_escape
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import Layout, Row, Column, Submit, Field

from djangotribune.settings_local import (TRIBUNE_MESSAGES_POST_MAX_LENGTH, TRIBUNE_MESSAGES_UA_COOKIE_NAME, 
                                            TRIBUNE_MESSAGES_UA_LENGTH_MIN, TRIBUNE_SAVE_URLS_BY_POST, 
                                            TRIBUNE_SESSION_MAX_OWNED_IDS)
from djangotribune.models import Channel, Message, Url
from djangotribune.parser import MessageParser
from djangotribune.actions import TRIBUNE_COMMANDS
from django.utils.timezone import utc

URLFILTERS_CHOICES = (
    ('url__contains', _('Url')),
    ('author__username__contains', _('Author')),
    ('message__raw__contains', _('Message')),
)

class UrlSearchForm(forms.Form):
    """
    Url archive search form
    """
    pattern = forms.CharField(label=_("Pattern"), max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': _("Search")}))
    filters = forms.MultipleChoiceField(label=_("Filters"), choices=URLFILTERS_CHOICES, required=True, widget=forms.CheckboxSelectMultiple)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            Row(
                Column(
                    'pattern',
                    css_class='eight mobile-two input-column'
                ),
                Column(
                    Field('filters', css_class='no-reset-click', wrapper_class="button expand dropdown postfix"),
                    css_class='three mobile-one input-column'
                ),
                Column(
                    Submit('post_submit', _('Ok'), css_class='tiny expand postfix'),
                    css_class='one mobile-one'
                ),
                css_class='collapse inline-form'
            ),
        )
        
        super(UrlSearchForm, self).__init__(*args, **kwargs)
    
    def save(self):
        """
        Return formatted search filters 
        """
        if hasattr(self, 'cleaned_data') and self.cleaned_data['pattern']:
            return [(item, self.cleaned_data['pattern']) for item in self.cleaned_data['filters']]
        return []

class MessageForm(forms.Form):
    """
    Message form
    """
    content = forms.CharField(label=_("Your message"), max_length=TRIBUNE_MESSAGES_POST_MAX_LENGTH, required=True, widget=forms.TextInput(attrs={
        'class':'content_field',
        'size':'50',
        'accesskey':'T'
    }))
    
    def __init__(self, headers, cookies, session, author, channel=None, *args, **kwargs):
        self.headers = headers
        self.cookies = cookies
        self.session = session
        self.channel = channel
        self.author = author
        self.parser = None
        self.command = None
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            Row(
                Column(
                    'content',
                    css_class='ten mobile-three input-column'
                ),
                Column(
                    Submit('post_submit', _('Ok'), css_class='expand postfix'),
                    css_class='two mobile-one'
                ),
                css_class='collapse'
            ),
        )
        
        super(MessageForm, self).__init__(*args, **kwargs)

    def clean_user_agent(self):
        """
        Get the user agent, either the browser user agent or the configured user agent 
        if any
        """
        try:
            uaBrowser = self.headers.get('HTTP_USER_AGENT', '').decode('utf-8')
        except:
            # For old application sending user agent in latin-1 ..
            uaBrowser = self.headers.get('HTTP_USER_AGENT', '').decode('latin-1')
        uaBrowser = uaBrowser.strip().replace('&nbsp;', '')
        
        # Select name from the name cookie if any
        uaCookie = self.cookies.get(TRIBUNE_MESSAGES_UA_COOKIE_NAME, False)
        if uaCookie and len(uaCookie)>2:
            from base64 import b64decode
            return html_escape( b64decode(uaCookie) )
        # Séléction de l'ua donnée dans le client
        else:
            if len(uaBrowser) < TRIBUNE_MESSAGES_UA_LENGTH_MIN:
                return "coward"
            return html_escape( uaBrowser )
    
    def clean_ip(self):
        """Get the client IP adress"""
        return self.headers.get('REMOTE_ADDR', None)
    
    def clean_content(self):
        """
        Content validation
        """
        content = self.cleaned_data['content']
        
        # Command validation and eventual pre-processing
        if content.startswith("/"):
            action_name = content.split(' ')[0][1:]
            actions = dict(TRIBUNE_COMMANDS)
            if action_name in actions:
                command = actions[action_name](content.split(' ')[1:], self.author, self.cookies, self.session)
                if command.validate():
                    self.command = command
        
        # Parse content only if it's not a command action or if the command need to push 
        # content
        if not self.command or self.command.need_to_push_data:
            self.parser = MessageParser()
            if not self.parser.validate(content):
                raise forms.ValidationError(_('Unvalid post content'))
        
        return content
    
    def clean(self):
        """Some suplementary validations after the global and field validations"""
        cleaned_data = self.cleaned_data
        cleaned_data['user_agent'] = self.clean_user_agent()
        cleaned_data['ip'] = self.clean_ip()
        
        return cleaned_data
    
    def save(self, *args, **kwargs):
        """
        Dispatch action depending on whether the content is a command action to execute 
        or a new message to save
        """
        # Excecute command and push message if any
        if self.command:
            self.command.execute()
            # If the action don't need to push data, simply return the action controller 
            # (eventually used to patch_response)
            if not self.command.need_to_push_data:
                return None
            # If the action need to push data, update the form datas to push a content
            else:
                self.cleaned_data.update( self.command.push_data(self.cleaned_data) )
        
        if self.parser:
            # Return the new saved message
            return self._save_message()
    
    def _save_message(self):
        """Save the new message"""
        new_message = None
        author = self.author
        rendered = self.parser.render(self.cleaned_data['content'])
        created = datetime.datetime.utcnow().replace(tzinfo=utc)
        
        if not author.is_authenticated():
            author = None
        
        new_message = Message(
            created=created,
            # Enforce the same time that the one stored in created
            clock=created.astimezone(pytz.timezone(settings.TIME_ZONE)).time(),
            channel=self.channel,
            author=author,
            user_agent=self.cleaned_data['user_agent'][:150],
            ip=self.cleaned_data['ip'],
            raw=self.cleaned_data['content'],
            web_render=rendered['web_render'],
            remote_render=rendered['remote_render'],
        )
        new_message.save()
        
        # If anonymous, save the id to a list (limited to X items) in session
        if author is None:
            owned_ids = self.session.get('tribune_owned_post_ids', [])[:TRIBUNE_SESSION_MAX_OWNED_IDS-1]
            owned_ids.insert(0, new_message.id)
            self.session['tribune_owned_post_ids'] = owned_ids
        # If authenticated, allways empty (to avoid conflict)
        else:
            self.session['tribune_owned_post_ids'] = []
        
        # If message contains URLs, archive them
        if rendered['urls']:
            self._save_urls(new_message, rendered['urls'])
        
        return new_message

    def _save_urls(self, message_instance, urls):
        """
        Save URLs finded in message content
        
        Check for unique url that did not allready exists in archives
        """
        # Unique urls limited on X url
        urls = set(urls[:TRIBUNE_SAVE_URLS_BY_POST])
        # Check those that have allready be saved
        allready_exists = Url.objects.filter(url__in=list(urls)).values_list('url', flat=True).distinct()
        # Filter urls to have only those are not saved yet
        urls = [item for item in urls if item not in allready_exists]
        # Save them
        for coming_url in urls:
            new_url = message_instance.url_set.create(
                author = message_instance.author,
                url = coming_url
            )
