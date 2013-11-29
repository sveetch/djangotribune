# -*- coding: utf-8 -*-
"""
Tribune command line
"""
import datetime, json, random, string

from optparse import OptionValueError, make_option

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import CommandError, BaseCommand
from django.contrib.auth.models import User

from djangotribune.parser import MessageParser
from djangotribune.models import Message

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--parse_again", action="store_true", dest="parse_again", default=False, help="Re-parse all raw content messages and re-save them with their result"),
    )
    help = "Command for doing stuff on djangotribune"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.parse_again = options.get('parse_again')
        
        if self.parse_again:
            self.do_parse_again()
        
    def do_parse_again(self):
        # Re-parse each message and re-save it
        for message in Message.objects.all().order_by('id'):
            parser = MessageParser()
            print message.id
            rendered = parser.render(message.raw)
            message.web_render = rendered['web_render']
            message.remote_render = rendered['remote_render']
            message.save()
        
        return