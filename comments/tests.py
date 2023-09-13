from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def test_comment(self):
        self.user = self.create_user("user1")
        self.tweet = self.create_tweet(self.user)
        self.comment = self.create_comment(self.user, self.tweet)
        self.assertNotEqual(self.comment.__str__(), None)
