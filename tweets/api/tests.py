from testing.testcases import TestCase
from rest_framework.test import APIClient
from tweets.models import Tweet

TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'


class TweetApiTests(TestCase):

    def setUp(self):
        # self.anonymous_client = APIClient()

        self.user1 = self.create_user('user1', 'user1@testing.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@testing.com')
        self.tweet2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]

    def test_list_api(self):
        # get method must have user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # usual request
        response = self.anonymous_client.get(
            TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        # print('response.data:', response.data)
        self.assertEqual(len(response.data['results']), 3)

        response = self.anonymous_client.get(
            TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['results']), 2)

        # test order by: recently posted tweets are displayed first
        # self.assertEqual(response.data['results'][0]['id'], self.tweets2[1].id)
        # self.assertEqual(response.data['results'][1]['id'], self.tweets2[0].id)

    def test_create_api(self):
        # must login
        response = self.anonymous_client.post(TWEET_LIST_API)
        self.assertEqual(response.status_code, 403)

        # must have content
        response = self.user1_client.post(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # content cannot be too short
        response = self.user1_client.post(TWEET_LIST_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content cannot be too long
        response = self.user1_client.post(TWEET_LIST_API, {
            'content': '1' * 141
        })
        self.assertEqual(response.status_code, 400)

        # normal posting
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            "content": "Hello World, this is my testing post"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)
