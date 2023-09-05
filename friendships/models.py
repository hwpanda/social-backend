from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Friendship(models.Model):

    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="following_friendship_set",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friend_set',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            # people I follow
            ('from_user_id', 'created_at'),
            # people follow me
            ('to_user_id', 'created_at'),
        )
        unique_together = (('from_user_id', 'to_user_id'),)

    def __str__(self):
        return f"{self.from_user} follows {self.to_user}"
