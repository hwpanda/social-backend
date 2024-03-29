from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.permissions import IsObjectOwner
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):

    # only list, create, update, destroy
    # don't need retrieve function for individual comment

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        """
        if 'tweet_id' not in request.query_params:
            return Response(
                {
                    'message': 'missing tweet_id in request',
                    'success': False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        """
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).prefetch_related(
            'user').order_by('created_at')
        serializer = CommentSerializer(
            comments,
            context={'request': request},
            many=True,
        )
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }

        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()

        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # get_object is function of DRF, will raise 404 error when not found
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save() will trigger update method in serializer
        # it check instance input to decide whether create or update
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    # delete
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF default destroy returns status code = 204 no content
        return Response({'success': True}, status=status.HTTP_200_OK)
