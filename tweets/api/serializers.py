from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Tweet
        field = '__all__'
