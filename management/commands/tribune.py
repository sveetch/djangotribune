# -*- coding: utf-8 -*-
"""
Tribune command line
"""
import json

from optparse import OptionValueError, make_option

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import CommandError, BaseCommand
from django.contrib.auth.models import User

from djangotribune.models import Message

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--build_test_attemps", dest="build_test_attemps", action="store_true", default=None, help="Print out some values to check in the unittests. For Development purpose only."),
    )
    help = "Command for Sveetchies-tribune"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.build_test_attemps = options.get('build_test_attemps')
        self.verbosity = int(options.get('verbosity'))
        
        if self.build_test_attemps:
            self.do_build_test_attemps()

    def do_build_test_attemps(self):
        """
        Create values to attempt in unittests
        """
        # Users
        superman = User.objects.get(username='superman')
        wonderwoman = User.objects.get(username='wonderwoman')
        
        # With anonymous
        base_total = Message.objects.orderize()
        base_from_10 = Message.objects.orderize(10)
        print "base_total =", list(base_total.flat())
        print "base_from_10 =", list(base_from_10.flat())
        print "base_from_10_limit_10 =", list(base_from_10[:10].flat())
        print
        
        # With superman
        #superman.filterentry_set.get_filters_args()
        superman_total = Message.objects.bunkerize(superman).orderize()
        superman_from_10 = Message.objects.bunkerize(superman).orderize(10)
        print "superman_total =", list(superman_total.flat())
        print "superman_from_10 =", list(superman_from_10.flat())
        print "superman_from_10_limit_10 =", list(superman_from_10[:10].flat())
        print
        
        # With wonderwoman
        #wonderwoman.filterentry_set.get_filters_args()
        wonderwoman_total = Message.objects.bunkerize(wonderwoman).orderize()
        wonderwoman_from_10 = Message.objects.bunkerize(wonderwoman).orderize(10)
        print "wonderwoman_total =", list(wonderwoman_total.flat())
        print "wonderwoman_from_10 =", list(wonderwoman_from_10.flat())
        print "wonderwoman_from_10_limit_10 =", list(wonderwoman_from_10[:10].flat())
        print