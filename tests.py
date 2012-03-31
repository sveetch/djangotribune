"""
Some tribune tests
"""
from django.test import TestCase
from django.contrib.auth.models import User

from djangotribune.models import Message

class MessagesAPITest(TestCase):
    """Test the queryset API to fetch messages"""
    def setUp(self):
        self.superman_user = User.objects.create(
            username='superman',
            first_name='clark',
            last_name='kent',
            email='superman@sveetch.biz',
            password='placeholder',
        )
        self.superman_user.filterentry_set.create(**{
            "kind": "exact", 
            "target": "author__username", 
            "value": "cassandre", 
        })
        
        self.wonderwoman_user = User.objects.create(
            username='wonderwoman',
            first_name='diana',
            last_name='prince',
            email='wonderwoman@sveetch.biz',
            password='placeholder',
        )
        self.wonderwoman_user.filterentry_set.create(**{
            "kind": "icontains", 
            "target": "user_agent", 
            "value": "Demokos", 
        })
        
    def test_01_anonymous(self):
        """test with anonymous"""
        base_total = Message.objects.bunkerize().orderize()
        base_from_10 = Message.objects.bunkerize().orderize(10)
        self.assertEqual(list(base_total.flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual(list(base_from_10.flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11])
        self.assertEqual(list(base_from_10[:10].flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 14])
        
    def test_02_superman(self):
        """test bunkerize with superman user"""
        base_total = Message.objects.bunkerize(self.superman_user).orderize()
        base_from_10 = Message.objects.bunkerize(self.superman_user).orderize(10)
        self.assertEqual(list(base_total.flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual(list(base_from_10.flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 13, 12, 11])
        self.assertEqual(list(base_from_10[:10].flat()), [23, 22, 21, 20, 19, 18, 17, 16, 15, 13])
        
    def test_02_wonderwoman(self):
        """test bunkerize with wonderwoman user"""
        base_total = Message.objects.bunkerize(self.wonderwoman_user).orderize()
        base_from_10 = Message.objects.bunkerize(self.wonderwoman_user).orderize(10)
        self.assertEqual(list(base_total.flat()), [23, 21, 19, 18, 16, 14, 13, 12, 11, 10, 9, 8, 7, 5, 3, 1])
        self.assertEqual(list(base_from_10.flat()), [23, 21, 19, 18, 16, 14, 13, 12, 11])
        self.assertEqual(list(base_from_10[:10].flat()), [23, 21, 19, 18, 16, 14, 13, 12, 11])

    def tearDown(self):
        pass
