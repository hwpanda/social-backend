from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate, TweetSerializerWithComments
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params


class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):

    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        # todo: with_all_comments
        # todo: with_preview_comments
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)

    @required_params(request_attr='query_params', params=['user_id'])
    def list(self, request):
        # if 'user_id' not in request.query_params:
        #     return Response('missing user_id', status=400)

        # user_id = request.query_params['user_id']

        # select * from socialMedia_tweets where user_id = xxx
        # order by created_at desc
        # tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        # serializer = TweetSerializer(tweets, many=True)

        # hash, not list
        # return Response({'tweets': serializer.data})
        # return Response({'results': serializer.data})
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializer.data})

    def create(self, request):
        # default current user
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)

        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet, context={'request': request}).data, status=201)
