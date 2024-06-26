from django.db import models
from datetime import datetime, time, timedelta, date
from django.core.exceptions import ValidationError
import dispatch_backend.validators as validators
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

alphanumeric = RegexValidator(r'^[0-9a-zA-Z-_]*$', 'Only alphanumeric characters or underscore or dash are allowed.')

START_TIME=time(8, 00, 00)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discord_id = models.CharField(max_length=65)

class Game(models.Model):
    name = models.CharField(max_length=100, validators=[alphanumeric])
    turn = models.IntegerField(default=1)
    start_time = models.TimeField(default=START_TIME)
    period_between_turns = models.IntegerField(default=15) #in minutes
    has_ended = models.BooleanField(default=False)
    server_id = models.BigIntegerField(blank=True, null=True)
    user_id = models.BigIntegerField(blank=True, null=True)
    show_sender_in_message = models.BooleanField(default=True)
    message_maximum_length = models.IntegerField(default=2000, validators=[MinValueValidator(0), MaxValueValidator(2000)])

    def __str__(self):
        return self.name

    def calculate_time(self):
        return (datetime.combine(date(1,1,1),self.start_time) + timedelta(minutes=(self.turn-1)*self.period_between_turns)).time()

    def clean(self):
        """ check that the name is not already taken by a current game """
        validators.validate_game(self, ValidationError)

    def get_categories(self):
        """ return list of categories"""
        return Category.objects.filter(game=self).values_list('number', flat=True)

    def get_channels(self):
        """ return list of channels"""
        return list(Channel.objects.filter(game=self).values_list('channel_id', flat=True))

class Channel(models.Model):
    name = models.CharField(max_length=100)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    channel_id = models.BigIntegerField()

    def __str__(self):
        return self.name

class Message(models.Model):
    text = models.TextField(max_length=2000)  # 2000 is the maximum length in discord
    date = models.DateTimeField(default=datetime.now)
    sender = models.CharField(max_length=100)
    turn_when_sent = models.IntegerField()
    turn_when_received = models.IntegerField(null=True, blank=True)
    is_lost = models.BooleanField(default=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    channels = models.ManyToManyField(Channel, related_name='message_channel')
    version = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.sender

    def clean(self):
        """ check if the message can be approved """
        validators.validate_message(self, ValidationError)

    def set_turn(self, turn):
        """ change the value for turn_when_received"""
        self.turn_when_received=turn
        self.save()


class SentMessage(Message):
    class Meta:
        proxy = True

class Category(models.Model):

    number = models.BigIntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return str(self.number)

    def clean(self):
        """ check that the category is not already in a current game """
        validators.validate_category(self, ValidationError)

class UserGameRelation(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "users"

    def __str__(self):
        return str(self.game.name) + ' : '+ str(self.user.username)