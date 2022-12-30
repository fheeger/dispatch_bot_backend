from django.contrib import admin
from .models import Message, Game, Channel, SentMessage, Category, UserGameRelation, User, Profile
from django.db.models import F
from django import forms
from django.contrib.auth.models import Group, User

class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        exclude = ()

    def __init__(self, *args, **kwargs):
        """ put relevant channels"""
        instance = kwargs.get('instance', None)
        super(MessageForm, self).__init__(*args, **kwargs)
        if instance and "channel" in self.fields:
            self.fields['channel'].choices = [('','------')]+[(channel.id, channel.name) for channel in Channel.objects.filter(game=instance.game)]
            self.fields['channel'].initial = instance.channel

class MessageAdmin(admin.ModelAdmin):
    list_display = ['game', 'turn_when_sent', 'sender', 'truncated_text', 'channel', 'turn_when_received', 'is_lost', 'approved']
    list_filter = ['approved', 'game__name', 'sender', 'is_lost']
    list_editable = ['channel', 'turn_when_received', 'is_lost', 'approved']
    form = MessageForm

    def get_changelist_form(self, request, **kwargs):
        return MessageForm

    def truncated_text(self, obj):
        """ show only the beginning of the text"""
        return obj.text[:60]

    def has_change_permission(self, request, obj=None):
        """ message sent and approved cannot be changed anymore"""
        if obj:
            return not obj.approved or obj.turn_when_received>obj.game.turn
        return True

    def get_queryset(self, request):
        queryset = self.model.objects.exclude(approved = True, turn_when_received__lte=F('game__turn'))
        list_games_id = UserGameRelation.objects.filter(user=request.user).values_list('game', flat=True)
        queryset = queryset.filter(game__in=list_games_id)
        return queryset


class SentMessageAdmin(MessageAdmin):
    list_editable=[]

    def get_queryset(self, request):
        queryset = self.model.objects.filter(approved = True, turn_when_received__lte=F('game__turn'))
        list_games_id = UserGameRelation.objects.filter(user=request.user).values_list('game', flat=True)
        queryset = queryset.filter(game__in=list_games_id)
        return queryset

class UserGameRelationInline(admin.StackedInline):
    model = UserGameRelation
    extra = 0

class CategoryInline(admin.StackedInline):
    model = Category
    extra = 0
    readonly_fields = ['number']

class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'turn', 'has_ended']
    list_filter = ['name', 'has_ended']
    inlines = [CategoryInline, UserGameRelationInline]
    readonly_fields = ['server_id', 'user_id']

class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'channel_id']
    list_filter = ['name', 'game']

class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    readonly_fields = ['discord_id']

class MyUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_superuser']
    inlines = [ProfileInline,]


admin.site.register(Message, MessageAdmin)
admin.site.register(SentMessage, SentMessageAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)