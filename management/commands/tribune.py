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
from djangotribune.actions import CommandBak
from djangotribune.bak import BakController
from djangotribune.test_parser import MESSAGE_TESTS
from djangotribune.parser import MessageParser
from djangotribune import TRIBUNE_BAK_SESSION_NAME

class FakeSession(dict):
    """Fake session via dict inherit just to add an dummy ``modified`` attribute"""
    def __init__(self, *args, **kwargs):
        super(FakeSession, self).__init__(*args, **kwargs)
        self.modified = False

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--build_test_attempts", dest="build_test_attempts", action="store_true", default=None, help="Print out some values to check in the unittests. For Development purpose only."),
        make_option("--test_parser", dest="test_parser", action="store_true", default=None, help="Test some parser rendering."),
        make_option("--bak", dest="test_bak", action="store_true", default=None, help="Temporary testing of Bak controller"),
    )
    help = "Command for Sveetchies-tribune"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.build_test_attempts = options.get('build_test_attempts')
        self.test_parser = options.get('test_parser')
        self.test_bak = options.get('test_bak')
        self.verbosity = int(options.get('verbosity'))
        
        if self.build_test_attempts:
            self.do_build_test_attempts()
        
        if self.test_parser:
            self.do_test_parser()

        if self.test_bak:
            self.do_test_bak()

    def do_test_bak(self):
        superman = User.objects.get(username='superman')
        bak_sup = BakController(superman)
        
        # Tricky fake session object for test
        self.fake_session = FakeSession()
        self.fake_session[TRIBUNE_BAK_SESSION_NAME] = bak_sup
        
        #self._do_test_action(['load'])
        
        print "==== UNVALIDS ===="
        self._do_test_action(['foo', 'author', 'todrop'])
        self._do_test_action(['add'])
        self._do_test_action(['set', 'author', 'todrop'])
        self._do_test_action(['set', 'hiddenfield', 'todrop'])
        self._do_test_action(['set', 'author', 'superRegex', 'todrop'])
        self._do_test_action(['set', 'hiddenfield', 'superRegex', 'todrop'])
        
        print "==== VALIDS ===="
        self._do_test_action(['set', 'ua', '|=', 'mozilla'])
        self._do_test_action(['set', 'message', '*=', 'kikoolol'])
        
        self._do_test_action(['add', 'author', 'todrop'])
        
        self._do_test_action(['del', 'author', 'todrop'])
        
        self._do_test_action(['remove', 'message', '*=', 'kikoolol'])
        
        #print bak_sup.get_filters()
        #self._do_test_action(['save'])
        
    def _do_test_action(self, command_args):
        print "_"*100
        print command_args
        commbak = CommandBak(command_args, [], {}, self.fake_session)
        
        is_valid = commbak.validate()
        print "is_valid:", is_valid
        if is_valid:
            commbak.execute()
            print ">>", commbak.controller.rules
            
        print

    def do_test_parser(self):
        """Temporary dummy parser test"""
        parser_instance = MessageParser()
        for serie_name, serie_tests in MESSAGE_TESTS.items():
            err = 0
            print "="*90
            print "Serie:", serie_name
            print "="*90
            for source, attempt in serie_tests:
                result = parser_instance.render(source)['web_render']
                if result != attempt:
                    err += 1
                print "- Attempt {0}:".format(type(attempt)), attempt
                print "- Rendered {0}:".format(type(result)), result
                print "-"*40
            print "Results : {0} / {1}".format(err, len(serie_tests))
            print

    def do_build_test_attempts(self):
        """
        Create values to attempt in unittests
        """
        # Users
        self.user_with_filter_1 = User.objects.get(username='user_with_filter_1')
        self.user_with_filter_2 = User.objects.get(username='user_with_filter_2')
        
        # With anonymous, with no channel filter
        base_total = Message.objects.orderize()
        base_from_10 = Message.objects.orderize(10)
        print "base_total =", list(base_total.flat())
        print "base_from_10 =", list(base_from_10.flat())
        print "base_from_10_limit_10 =", list(base_from_10[:10].flat())
        print
        
        # With anonymous, with default channel filter
        default_chan_total = Message.objects.orderize().from_chan()
        default_chan_from_10 = Message.objects.orderize(10).from_chan()
        #backend_default_chan_total = Message.objects.orderize().from_chan()
        print "default_chan_total =", list(default_chan_total.flat())
        print "default_chan_from_10 =", list(default_chan_from_10.flat())
        print "default_chan_from_10_limit_10 =", list(default_chan_from_10[:10].flat())
        print
        
        # With superman
        #self.user_with_filter_1.filterentry_set.get_filters_kwargs()
        user_with_filter_1_total = Message.objects.from_chan("troie").bunkerize(self.user_with_filter_1).orderize()
        user_with_filter_1_from_10 = Message.objects.from_chan("troie").bunkerize(self.user_with_filter_1).orderize(10)
        print "user_with_filter_1_total =", list(user_with_filter_1_total.flat())
        print "user_with_filter_1_from_10 =", list(user_with_filter_1_from_10.flat())
        print "user_with_filter_1_from_10_limit_10 =", list(user_with_filter_1_from_10[:10].flat())
        print
        
        # With wonderwoman
        #self.user_with_filter_2.filterentry_set.get_filters_kwargs()
        user_with_filter_2_total = Message.objects.from_chan("troie").bunkerize(self.user_with_filter_2).orderize()
        user_with_filter_2_from_10 = Message.objects.from_chan("troie").bunkerize(self.user_with_filter_2).orderize(10)
        print "user_with_filter_2_total =", list(user_with_filter_2_total.flat())
        print "user_with_filter_2_from_10 =", list(user_with_filter_2_from_10.flat())
        print "user_with_filter_2_from_10_limit_10 =", list(user_with_filter_2_from_10[:10].flat())
        print