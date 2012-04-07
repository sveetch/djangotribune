# -*- coding: utf-8 -*-
"""
Forms
"""
from django import forms
from django.utils.html import escape as html_escape

from djangotribune import TRIBUNE_MESSAGES_POST_MAX_LENGTH, TRIBUNE_MESSAGES_UA_COOKIE_NAME, TRIBUNE_MESSAGES_UA_LENGTH_MIN
from djangotribune.models import Channel, Message, Url
from djangotribune.parser import MessageParser
from djangotribune.actions import TRIBUNE_COMMANDS

class ContentMessageWidget(forms.TextInput):
    """
    Message content widget
    
    This put a field with all medias related to his usage
    """
    input_type = 'text'
    
    def _media(self):
        """
        Adds necessary files (Js/CSS) to the widget's medias
        """
        css_items = []
        js_items = []
        
        return forms.Media(
            css={'all': tuple(css_items)},
            js=tuple(js_items),
        )
    media = property(_media)

class MessageForm(forms.Form):
    """
    Message form
    """
    content = forms.CharField(max_length=TRIBUNE_MESSAGES_POST_MAX_LENGTH, required=True, widget=ContentMessageWidget(attrs={'size':'50', 'accesskey':'T'}))
    
    def __init__(self, headers, cookies, session, author, channel=None, *args, **kwargs):
        self.headers = headers
        self.cookies = cookies
        self.session = session
        self.channel = channel
        self.author = author
        self.parser = None
        self.command = None
        
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
        # If it's a validated command action, don't proceed with the parser
        if content.startswith("/"):
            action_name = content.split(' ')[0][1:]
            actions = dict(TRIBUNE_COMMANDS)
            if action_name in actions:
                command = actions[action_name](content.split(' ')[1:])
                if command.validate():
                    self.command = command
                    return content
        
        # Parse content only if it's not a valid command action
        self.parser = MessageParser()
        if not self.parser.validate(content):
            raise forms.ValidationError(u'Unvalid post content')
        
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
        if self.parser:
            # Return the new saved message
            return self._save_message()
        else:
            # Return the command action instance
            self.command.execute()
            return self.command
    
    def _save_message(self):
        """Save the new message"""
        new_message = None
        author = self.author
        rendered = self.parser.render(self.cleaned_data['content'])
        
        if not author.is_authenticated():
            author = None
        
        new_message = Message(
            channel=self.channel,
            author=author,
            user_agent=self.cleaned_data['user_agent'][:150],
            ip=self.cleaned_data['ip'],
            raw=self.cleaned_data['content'],
            web_render=rendered['web_render'],
            remote_render=rendered['remote_render'],
        )
        new_message.save()
        if rendered['urls']:
            self._save_urls(new_message, rendered['urls'])
        
        return new_message

    def _save_urls(self, message_instance, urls):
        """Save URLs finded in message content"""
        SAVE_URLS_BY_POST = 5 # limit
        l = []
        for coming_url in urls[:SAVE_URLS_BY_POST]:
            if coming_url not in l:
                new_url = message_instance.url_set.create(
                    author = message_instance.author,
                    url = coming_url
                )
                l.append(coming_url)
