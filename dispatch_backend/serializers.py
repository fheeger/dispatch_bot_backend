from rest_framework import serializers
from .models import Game, Channel, Message, Category, Profile, UserGameRelation
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
    showSender = serializers.ReadOnlyField(source="game.show_sender_in_message")
    channels_list = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("sender", "showSender", "channels_list", "text", "turn_when_sent", "turn_when_received", "game")

    def get_channels_list(self, obj):
        return [{'channelId':channel.channel_id, 'channelName':channel.name} for channel in obj.channels.all()]

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

class UserGameRelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGameRelation
        fields = ("user", "game")
