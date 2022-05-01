from rest_framework import serializers, exceptions
from .models import Game, Channel, Message, Category


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