from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet
from django.contrib.contenttypes.models import ContentType
from likes.models import Like


class Comment(models.Model):

    # basic comments
    # only make comments on tweet, not comments
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    tweet = models.ForeignKey(Tweet, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('tweet', 'created_at'), )

    def __str__(self):

        return f"{self.created_at} - {self.user} says {self.content} at tweet {self.tweet_id}"

    @property
    def like_set(self):
        # tweet.like_set() to get all likes for this tweet
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        ).order_by('-created_at')
