from django.contrib import admin, messages
from django.db import models
from django.forms import SelectMultiple

import dispatch_backend
from .forms import MessageForm
from .models import Message, Game, Channel, SentMessage, Category, UserGameRelation, Profile
from django.db.models import F
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.views.main import ChangeList

class MessageChangeList(ChangeList):

    def __init__(self,  *args, **kwargs):
        super(MessageChangeList, self).__init__(*args, **kwargs)
        self.list_display = ['id', 'game', 'turn_when_sent', 'sender', 'truncated_text', 'channels', 'version', 'turn_when_received', 'is_lost', 'approved']
        self.list_editable = ['turn_when_received', 'is_lost', 'approved', 'version', 'channels']
        self.list_display_links = ['game']

class MessageAdmin(admin.ModelAdmin):
    form = MessageForm
    list_filter = ['approved', 'game__name', 'sender', 'is_lost']

    def get_changelist(self, request, **kwargs):
        return MessageChangeList

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

    def save_related(self, request, form, formsets, change):
        print(form.cleaned_data)
        if not form.cleaned_data["approved"] or len(form.cleaned_data["channels"])>0:
            super().save_related(request, form, formsets, change)
        else:
            messages.error(
                request, "Message {}: the channels cannot be empty when the message is approved".format(form.instance.id))

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        user_version = form.cleaned_data["version"]
        try:
            db_version = self.model.objects.get(id=obj.id).version
        except dispatch_backend.models.Message.DoesNotExist:
            db_version = user_version

        if db_version != user_version:
            messages.warning(
                request,
                "Message {} has been changed since you loaded it and could not be modified.".format(obj.id)
            )
        elif form.cleaned_data["approved"] and len(form.cleaned_data["channels"]) == 0:
            messages.error(
                request,
                "Message {} has can only be approved if at least one channel is chosen.".format(obj.id)
            )
        else:
            obj.version += 1
            obj.turn_when_received = form.cleaned_data["turn_when_received"]
            obj.is_lost = form.cleaned_data["is_lost"]
            obj.approved = form.cleaned_data["approved"]
            super().save_model(request, obj, form, change)


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