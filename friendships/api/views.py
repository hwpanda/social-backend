from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # POST /api/friendship/1/follow is to follow user_id=1
    # so we query User, instead of Friendship
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate

    def list(self, request):
        # GET /api/friendships/
        return Response({'message': 'this is friendships page'})

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers/
        friendships = Friendship.objects.filter(
            to_user_id=pk).order_by("-created_at")
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        # GET /api/friendships/1/following/
        friendships = Friendship.objects.filter(
            from_user_id=pk).order_by("-created_at")
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {'following': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # check repeat follow, like click multiple times
        # ignore

        # self.get_object()
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            "from_user_id": request.user.id,
            "to_user_id": pk,
        })

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        return Response(
            {'success': True},
            status=status.HTTP_201_CREATED
        )

    # https://docs.djangoproject.com/en/4.2/ref/models/querysets/#delete
    # Performs an SQL delete query on all rows in the QuerySet and returns the number of objects deleted and a dictionary with the number of deletions per object type.
    # The delete() is applied instantly. You cannot call delete() on a QuerySet that has had a slice taken or can otherwise no longer be filtered.
    # By default, Django’s ForeignKey emulates the SQL constraint ON DELETE CASCADE — in other words, any objects with foreign keys pointing at the objects to be deleted will be deleted along with them; domino effect

    # ! CASCADE is dangerous, so use on_delete=models.SET_NULL

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        unfollow_user = self.get_object()
        if request.user.id == int(unfollow_user.id):
            return Response({
                'success': False,
                'message': "You cannot unfollow yourself",
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollow_user,
        ).delete()

        return Response({
            'success': True,
            'deleted': deleted,
        }, status=status.HTTP_200_OK)
