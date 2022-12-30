from django.contrib import admin
from .models import Message, Game, Channel, SentMessage, Category, UserGameRelation, User, Profile
from django.db.models import F
from django import forms
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

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

    def get_queryset(self, request):
        if request.user.is_superuser:
            return self.model.objects.all()
        list_games_id = UserGameRelation.objects.filter(user=request.user).values_list('game', flat=True)
        queryset = self.model.objects.filter(id__in=list_games_id)
        return queryset

class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'channel_id']
    list_filter = ['name', 'game']

class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    readonly_fields = ['discord_id']

class MyUserAdmin(UserAdmin):
    list_display = ['username', 'is_superuser']
    inlines = [ProfileInline,]

    def get_fieldsets(self, request, obj=None):
        if request.user and request.user.is_superuser:
            fieldsets =  UserAdmin.fieldsets
            self.inlines = [ProfileInline,]
        else:
            fieldsets = (
                (None, {'fields': ('username', 'password')}),
            )
            self.inlines = []
        return fieldsets


    def get_queryset(self, request):
        if request.user.is_superuser:
            queryset = self.model.objects.all()
        else:
            queryset = self.model.objects.filter(id=request.user.id)
        return queryset

admin.site.register(Message, MessageAdmin)
admin.site.register(SentMessage, SentMessageAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)