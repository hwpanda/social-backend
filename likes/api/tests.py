from rest_framework.test import APIClient

from testing.testcases import TestCase

LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_API = '/api/comments/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


class LikeApiTests(TestCase):

    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client('user1')
        self.user2, self.user2_client = self.create_user_and_client('user2')

    def test_tweet_likes(self):
        tweet = self.create_tweet(self.user1)
        data = {'content_type': 'tweet', 'object_id': tweet.id}

        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.post(
            LIKE_BASE_URL, {'content_type': 'twet', 'object_id': tweet.id})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(
            LIKE_BASE_URL, {'content_type': 'tweet', 'object_id': -1})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_tweet_comments(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        data = {'content_type': 'comment', 'object_id': comment.id}

        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.post(
            LIKE_BASE_URL, {'content_type': 'coment', 'object_id': comment.id})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(
            LIKE_BASE_URL, {'content_type': 'comment', 'object_id': -1})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 1)
        self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        tweet_data = {'content_type': 'tweet', 'object_id': tweet.id}
        comment_data = {'content_type': 'comment', 'object_id': comment.id}
        self.user1_client.post(LIKE_BASE_URL, comment_data)
        self.user2_client.post(LIKE_BASE_URL, tweet_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        response = self.anonymous_client.post(LIKE_CANCEL_URL, comment_data)
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.get(LIKE_CANCEL_URL, comment_data)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.post(
            LIKE_CANCEL_URL, {'content_type': 'coment', 'object_id': comment.id})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(
            LIKE_CANCEL_URL, {'content_type': 'comment', 'object_id': -1})
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(LIKE_CANCEL_URL, comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.like_set.count(), 1)
        self.assertEqual(tweet.like_set.count(), 1)

        response = self.user1_client.post(LIKE_CANCEL_URL, comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.like_set.count(), 0)
        self.assertEqual(tweet.like_set.count(), 1)

        response = self.user1_client.post(LIKE_CANCEL_URL, tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.like_set.count(), 0)
        self.assertEqual(tweet.like_set.count(), 1)

        response = self.user2_client.post(LIKE_CANCEL_URL, tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.like_set.count(), 0)
        self.assertEqual(tweet.like_set.count(), 0)

    def test_likes_in_comments_api(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)

        # test anonymous
        response = self.anonymous_client.get(
            COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)

        # test comments list api
        response = self.user2_client.get(
            COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.user2, comment)
        response = self.user2_client.get(
            COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # test tweet detail api
        self.create_like(self.user1, comment)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 2)

    def test_likes_in_tweets_api(self):
        tweet = self.create_tweet(self.user1)

        # test tweet detail api
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
        self.create_like(self.user2, tweet)
        response = self.user2_client.get(url)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 1)

        # test tweet list api
        response = self.user2_client.get(
            TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tweets'][0]['has_liked'], True)
        self.assertEqual(response.data['tweets'][0]['likes_count'], 1)

        # test newsfeeds list api
        self.create_like(self.user1, tweet)
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['newsfeeds']
                         [0]['tweet']['has_liked'], True)
        self.assertEqual(response.data['newsfeeds']
                         [0]['tweet']['likes_count'], 2)

        # test likes details
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(len(response.data['likes']), 2)
        self.assertEqual(response.data['likes']
                         [0]['user']['id'], self.user1.id)
        self.assertEqual(response.data['likes']
                         [1]['user']['id'], self.user2.id)
