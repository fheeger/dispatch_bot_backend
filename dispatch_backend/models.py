from django.db import models
from datetime import datetime, time, timedelta, date
from django.core.exceptions import ValidationError
import dispatch_backend.validators as validators
from django.core.validators import RegexValidator

alphanumeric = RegexValidator(r'^[0-9a-zA-Z-_]*$', 'Only alphanumeric characters or underscore or dash are allowed.')

START_TIME=time(8, 00, 00)

class Game(models.Model):
    name = models.CharField(max_length=100, validators=[alphanumeric])
    turn = models.IntegerField(default=1)
    start_time = models.TimeField(default=START_TIME)
    period_between_turns = models.IntegerField(default=15) #in minutes
    has_ended = models.BooleanField(default=False)
    server_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def calculate_time(self):
        return (datetime.combine(date(1,1,1),self.start_time) + timedelta(minutes=(self.turn-1)*self.period_between_turns)).time()

    def clean(self):
        """ check that the name is not already taken by a current game """
        validators.validate_game(self, ValidationError)

class Channel(models.Model):
    name = models.CharField(max_length=100)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Message(models.Model):
    text = models.TextField(max_length=2000)
    date = models.DateTimeField(default=datetime.now)
    sender = models.CharField(max_length=100)
    turn_when_sent = models.IntegerField()
    turn_when_received = models.IntegerField(null=True, blank=True)
    is_lost = models.BooleanField(default=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True, blank=True)

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

    number = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.number


