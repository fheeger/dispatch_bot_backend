from django.contrib import admin
from .models import Message, Game, Channel

class MessageAdmin(admin.ModelAdmin):
    list_display = ['game', 'turn_when_sent', 'sender', 'text', 'channel', 'turn_when_received', 'is_lost', 'approved']
    list_filter = ['approved', 'game__name', 'turn_when_sent', 'sender', 'turn_when_received', 'is_lost']
    list_editable = ['channel', 'turn_when_received', 'is_lost', 'approved']

class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'turn']
    list_filter = ['name']

class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'game']
    list_filter = ['name']


admin.site.register(Message, MessageAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Channel, ChannelAdmin)