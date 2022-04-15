from django.contrib import admin
from .models import Message, Game, Channel, SentMessage


class MessageAdmin(admin.ModelAdmin):
    list_display = ['game', 'turn_when_sent', 'sender', 'truncated_text', 'channel', 'turn_when_received', 'is_lost', 'approved']
    list_filter = ['approved', 'game__name', 'sender', 'is_lost']
    list_editable = ['channel', 'turn_when_received', 'is_lost', 'approved']

    def truncated_text(self, obj):
        """ show only the beginning of the text"""
        return obj.text[:60]

    def has_change_permission(self, request, obj=None):
        """ message sent and approved cannot be changed anymore"""
        if obj:
            return not obj.approved or obj.turn_when_received>obj.game.turn
        return True

    def get_queryset(self, request):
        game = Game.objects.latest('id')
        return self.model.objects.exclude(approved = True, turn_when_received__lt=game.turn)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ only show channels of last game
        warning : with show it for all messages even from previous game"""
        if db_field.name == "channel":
            try:
                game = Game.objects.latest('id')
                kwargs["queryset"] = Channel.objects.filter(game=game)
            except:
                kwargs["queryset"] = Channel.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SentMessageAdmin(MessageAdmin):
    list_editable=[]
    def get_queryset(self, request):
        game = Game.objects.latest('id')
        return self.model.objects.filter(approved = True, turn_when_received__lt=game.turn)

class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'turn', 'has_ended']
    list_filter = ['name', 'has_ended']

class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'game']
    list_filter = ['name']


admin.site.register(Message, MessageAdmin)
admin.site.register(SentMessage, SentMessageAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Channel, ChannelAdmin)