from friendships.models import Friendship
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from testing.testcases import TestCase
from rest_framework.test import APIClient


NEWSFEED_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):

        self.user1 = self.create_user("user1")
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user("user2")
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        # create following and followers for user2
        for i in range(2):
            follower = self.create_user('user2_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user('user2_following{}'.format(i))
            Friendship.objects.create(from_user=self.user2, to_user=following)

    def test_list(self):
        response = self.anonymous_client.get(NEWSFEED_URL)
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.post(NEWSFEED_URL)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.get(NEWSFEED_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

        self.user1_client.post(POST_TWEETS_URL, {'content': "Hello World"})
        response = self.user1_client.get(NEWSFEED_URL)
        self.assertEqual(len(response.data['results']), 1)

        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(
            POST_TWEETS_URL, {'content': "Hello World"})
        posted_tweet_id = response.data["id"]
        response = self.user1_client.get(NEWSFEED_URL)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results']
                         [0]['tweet']['id'], posted_tweet_id)
