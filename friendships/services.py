from friendships.models import Friendship


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # leads to N+1 Queries problem
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.form_user for friendship in friendships]

        # select_related will be translated as 'JOIN' in query, slow
        # friendships = Friendship.objects.filter(to_user=user).select_related('from_user')
        # return [friendship.form_user for friendship in friendships]

        # add filter id, by IN Query
        # friendship = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # prefetch_related
        friendships = Friendship.objects.filter(
            to_user=user, ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]
