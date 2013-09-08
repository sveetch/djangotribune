# -*- coding: utf-8 -*-
"""
Some tribune tests
"""
import datetime

from django.test import TestCase

from djangotribune.parser import PostCleaner
from djangotribune.clocks import ClockParser

class ParserTest(TestCase):
    """Test the message parser"""
    def test_show_truncated_url(self):
        # TODO: invalid test, assertEqual fail because of encoding 
        # differences with '…' characters
        link = 'http://example.com/' + 200*'a' + '/b/'
        pc = PostCleaner(link)
        truncated = pc.truncate_link('http', link)
        self.assertEqual(truncated, 'example.com/' + 85*'a' + '…')


class ClockParserTest(TestCase):
    """Test the clock parser"""
    def setUp(self):
        self.parser = ClockParser()

    def test_01_valid_unvalid(self):
        """Various invalid stuff to test"""
        self.assertFalse(self.parser.is_valid('foo'))
        self.assertFalse(self.parser.is_valid('foo:coco'))
        self.assertFalse(self.parser.is_valid('1200'))
        self.assertFalse(self.parser.is_valid('12001'))
        self.assertFalse(self.parser.is_valid('1200^1'))
        self.assertFalse(self.parser.is_valid('12001^1'))

    def test_02_valid_simple_clock(self):
        """Simple clocks"""
        # These ones should valid
        self.assertTrue(self.parser.is_valid('00:00'))
        self.assertTrue(self.parser.is_valid('12:00'))
        self.assertTrue(self.parser.is_valid('23:59'))
        self.assertTrue(self.parser.is_valid('03:57'))
        # These ones should not valid
        self.assertFalse(self.parser.is_valid('33:57'))
        self.assertFalse(self.parser.is_valid('12:67'))

    def test_03_valid_full_clock(self):
        """Full clocks"""
        # These ones should valid
        self.assertTrue(self.parser.is_valid('000000'))
        self.assertTrue(self.parser.is_valid('235959'))
        self.assertTrue(self.parser.is_valid('00:00:00'))
        self.assertTrue(self.parser.is_valid('12:00:00'))
        self.assertTrue(self.parser.is_valid('23:59:59'))
        self.assertTrue(self.parser.is_valid('03:57:12'))
        # These ones should not valid
        self.assertFalse(self.parser.is_valid('33:57:14'))
        self.assertFalse(self.parser.is_valid('12:67:01'))
        self.assertFalse(self.parser.is_valid('12:13:77'))

    def test_04_valid_full_clock_with_indice(self):
        """Full clocks with indice"""
        # These ones should valid
        self.assertTrue(self.parser.is_valid('000000^1'))
        self.assertTrue(self.parser.is_valid('235959^1'))
        self.assertTrue(self.parser.is_valid('00:00:00^1'))
        self.assertTrue(self.parser.is_valid('12:00:00^11'))
        self.assertTrue(self.parser.is_valid('23:59:59^35'))
        self.assertTrue(self.parser.is_valid('03:57:12^3'))
        # TODO: These ones should not be valid, the regex ignore them but if ^ is used 
        # it should raise error if not a valid integer
        self.assertTrue(self.parser.is_valid('13:57:14^'))
        self.assertTrue(self.parser.is_valid('12:57:01^sss'))
        self.assertTrue(self.parser.is_valid('12:13:57^a'))
        # These ones should not valid
        self.assertFalse(self.parser.is_valid('33:57:14^1'))
        self.assertFalse(self.parser.is_valid('12:67:01^12'))
        self.assertFalse(self.parser.is_valid('12:13:77^5'))

    def test_05_parse(self):
        """Test parser method"""
        # Invalid stuff
        self.assertRaises(TypeError, self.parser.parse, 'foo')
        self.assertRaises(TypeError, self.parser.parse, 'foo:coco')
        self.assertRaises(TypeError, self.parser.parse, '33:57')
        # Valid stuff
        self.assertEqual(self.parser.parse('12:45'), {'hour': 12, 'minute': 45, 'second': 0, 'indice': 0, 'microsecond': 0})
        self.assertEqual(self.parser.parse('23:59:13'), {'hour': 23, 'minute': 59, 'second': 13, 'indice': 0, 'microsecond': 0})
        self.assertEqual(self.parser.parse('23:59:13^42'), {'hour': 23, 'minute': 59, 'second': 13, 'indice': 42, 'microsecond': 0})

    def test_06_time_object(self):
        """Test clock time object"""
        self.assertEqual(self.parser.get_time_object('12:45'), datetime.time(12, 45))
        self.assertEqual(self.parser.get_time_object('12:45^1'), datetime.time(12, 45))
        self.assertEqual(self.parser.get_time_object('23:59:13'), datetime.time(23, 59, 13))
        self.assertEqual(self.parser.get_time_object('23:59:13^1'), datetime.time(23, 59, 13))
