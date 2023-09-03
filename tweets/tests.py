from django.test import TestCase
from django.contrib.auth.models import User
from datatime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def test_hours_to_now(self):
        testUser = User.objects.create_user(username='testUser')
        tweet = Tweet.objects.create(user=testUser, content='this is a test')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
