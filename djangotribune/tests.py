"""
Some tribune tests
"""
from django.test import TestCase
from django.contrib.auth.models import User

from djangotribune.models import Message
from djangotribune.parser import PostCleaner

class MessagesAPITest(TestCase):
    """Test the queryset API to fetch messages"""
    def setUp(self):
        self.user_with_filter_1 = User.objects.get(username='user_with_filter_1')
        self.user_with_filter_2 = User.objects.get(username='user_with_filter_2')
        
    def test_01_base(self):
        """test from anonymous on all channels with no filters"""
        base_total = Message.objects.bunkerize().orderize()
        base_from_10 = Message.objects.bunkerize().orderize(10)
        self.assertEqual(list(base_total.flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual(list(base_from_10.flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11])
        self.assertEqual(list(base_from_10[:10].flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 14])
        
    def test_03_filters(self):
        """test bunkerize with user message filters 1 on channel 'troie'"""
        base_total = Message.objects.bunkerize(self.user_with_filter_1).orderize()
        base_from_10 = Message.objects.bunkerize(self.user_with_filter_1).orderize(10)
        self.assertEqual(list(base_total.flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual(list(base_from_10.flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 13, 12, 11])
        self.assertEqual(list(base_from_10[:10].flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 13])
        
    def test_04_filters(self):
        """test bunkerize with user message filters 2 on channel 'troie'"""
        base_total = Message.objects.bunkerize(self.user_with_filter_2).orderize()
        base_from_10 = Message.objects.bunkerize(self.user_with_filter_2).orderize(10)
        self.assertEqual(list(base_total.flat()), [23, 21, 19, 18, 16, 14, 13, 12, 11, 10, 9, 8, 7, 5, 3, 1])
        self.assertEqual(list(base_from_10.flat()), [23, 21, 19, 18, 16, 14, 13, 12, 11])
        self.assertEqual(list(base_from_10[:10].flat()), [23, 21, 19, 18, 16, 14, 13, 12, 11])

    def tearDown(self):
        pass


class ParserTest(TestCase):

    def test_show_truncated_url(self):
        link = 'http://example.com/' + 200*'a' + '/b/'
        pc = PostCleaner(link)
        truncated = pc.truncate_link('http', link)
        self.assertEqual(truncated, 'example.com/' + 85*'a' + '...')
