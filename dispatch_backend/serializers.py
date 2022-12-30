from rest_framework import serializers, exceptions
from .models import Game, Channel, Message, Category, Profile
from django.core.exceptions import ValidationError
from .validators import validate_category
from django.contrib.auth.models import User

class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ("turn","name", "start_time", "server_id", "user_id")


class ChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = ("name", "game", "channel_id")


class MessageSerializer(serializers.ModelSerializer):
    channelName = serializers.ReadOnlyField(source="channel.name")

    class Meta:
        model = Message
        fields = ("sender", "channelName", "text", "turn_when_sent", "turn_when_received", "game")

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ("number", "game")

    def validate(self, data):
        instance = Category(**data)
        validate_category(instance, serializers.ValidationError)
        return data

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "is_staff")

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("user", "discord_id")
