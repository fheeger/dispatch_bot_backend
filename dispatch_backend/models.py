from django.db import models
from datetime import datetime, time, timedelta, date


START_TIME=time(8, 00, 00)

class Game(models.Model):
    name = models.CharField(max_length=100)
    turn = models.IntegerField(default=1)
    start_time = models.TimeField(default=START_TIME)
    period_between_turns = models.IntegerField(default=15) #in minutes

    def __str__(self):
        return self.name

    def calculate_time(self):
        return (datetime.combine(date(1,1,1),self.start_time) + timedelta(minutes=(self.turn-1)*self.period_between_turns)).time()

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





