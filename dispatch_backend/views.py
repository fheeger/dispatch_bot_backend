from rest_framework import viewsets, status
from rest_framework.permissions import  AllowAny
from .models import Message, Game
from .serializers import GameSerializer, ChannelSerializer, MessageSerializer
from rest_framework.response import Response

class get_round(viewsets.ModelViewSet):
    """ show list of encryption types"""
    permission_classes = (AllowAny,)
    serializer_class = GameSerializer

    def get_object(self):
        """ return the list of user types as dict """
        game = Game.objects.latest('id')
        return game

    def partial_update(self, request, pk=None):
        game = Game.objects.latest('id')
        game.turn += 1
        game.save()
        data =  {'name':game.name,
                'turn': game.turn,
                'current_time' : game.calculate_time()}

        return Response(data,status=status.HTTP_200_OK)


class new_game(viewsets.ModelViewSet):
    """ show list of encryption types"""
    permission_classes = (AllowAny,)
    serializer_class = GameSerializer

    def create_game(self, request, *args, **kwargs):
        """ create a new game and new channels """
        serializer = GameSerializer(data={'name':request.data['name_game']}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        for channel in request.data['name_channels']:
            channel_serializer=ChannelSerializer(data={'name':channel, 'game':game.id}, context={'request': request})
            channel_serializer.is_valid(raise_exception=True)
            channel_serializer.save()
        return Response(serializer.data, status=201)

class get_messages(viewsets.ModelViewSet):
    """ get list of messages"""
    permission_classes = (AllowAny,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        """ list of messages """
        game = Game.objects.latest('id')
        messages = Message.objects.filter(game=game, approved=True, turn_when_received=game.turn, is_lost=False)
        return messages

class new_message(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = MessageSerializer

    def create_message(self, request, *args, **kwargs):
        print(request.data)
        data = request.data.copy()
        game = Game.objects.latest('id')
        data["turn_when_sent"] = game.turn
        data["turn_when_received"] = game.turn+1
        data["game"] = game.id
        print(data)
        serializer = MessageSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        print(serializer.data)
        return Response(serializer.data, status=201)

class check_messages(viewsets.ModelViewSet):
    """ get list of messages"""
    permission_classes = (AllowAny,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        """ list of messages for the next turn that was not approved yet"""
        game = Game.objects.latest('id')
        messages = Message.objects.filter(game=game, approved=False, turn_when_received=game.turn+1)
        return messages
