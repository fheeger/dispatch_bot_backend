from rest_framework import viewsets, status
from rest_framework.permissions import  AllowAny
from .models import Message, Game, Category
from .serializers import GameSerializer, ChannelSerializer, MessageSerializer, CategorySerializer
from rest_framework.response import Response

def get_game(request, game_name=None):
    server_id = None
    category_id = None
    if request.POST:
        server_id = request.POST.get('server_id', None)
        category_id = request.POST.get('category_id', None)
    elif request.GET:
        server_id = request.GET.get('server_id', None)
        category_id = request.GET.get('category_id', None)
    if server_id:
        games = Game.objects.filter(has_ended=False, server_id=server_id)
    else:
        games = Game.objects.filter(has_ended=False)
    if game_name:
        games = games.filter(name=game_name)
    if not category_id:
        return games.latest('id')
    for game in games:
        if category_id in game.get_categories():
            return game

    return None

class get_round(viewsets.ModelViewSet):
    """ show list of encryption types"""
    permission_classes = (AllowAny,)
    serializer_class = GameSerializer

    def get_object(self):
        """ return the list of user types as dict """
        return get_game(self.request)

    def partial_update(self, request, pk=None):
        game=get_game(self.request)
        if not game:
            return Response({'error': 'There is no game'},status=status.HTTP_200_OK)
        game.turn += 1
        game.save()
        data =  {'name':game.name,
                'turn': game.turn,
                'current_time' : game.calculate_time()}
        for message in Message.objects.filter(approved=False, turn_when_received=game.turn-1):
            message.set_turn(game.turn)
        return Response(data,status=status.HTTP_200_OK)


class new_game(viewsets.ModelViewSet):
    """ show list of encryption types"""
    permission_classes = (AllowAny,)
    serializer_class = GameSerializer

    def create_game(self, request, *args, **kwargs):
        """ create a new game and new channels """
        if len(Game.objects.filter(has_ended=False, name=request.data['name_game'])) >= 1:
            return Response({'error': 'A game with the same name is already going on! Please choose another name'},status=status.HTTP_200_OK)
        serializer = GameSerializer(data={'name':request.data['name_game'],
                                          'server_id': request.data['server_id'],
                                          'user_id' : request.data['user_id']}, context={'request': request})
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
        game = get_game(self.request)
        if not game:
            return []
        messages = Message.objects.filter(game=game, approved=True, turn_when_received=game.turn, is_lost=False)
        return messages

class new_message(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = MessageSerializer

    def create_message(self, request, *args, **kwargs):
        game = get_game(self.request)
        if not game:
            return Response({'error': 'There is no game'},status=status.HTTP_200_OK)
        data = request.data.copy()
        data["turn_when_sent"] = game.turn
        data["turn_when_received"] = game.turn+1
        data["game"] = game.id
        list_categories = data.pop('category')
        serializer = MessageSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        for category in list_categories:
            category_serializer = CategorySerializer(data={'number': category,
                                                           'game':game}, context={'request': request})
            category_serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=201)

class check_messages(viewsets.ModelViewSet):
    """ get list of messages"""
    permission_classes = (AllowAny,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        """ list of messages for the next turn that was not approved yet"""
        game = get_game(self.request)
        if not game:
            return []
        messages = Message.objects.filter(game=game, approved=False, turn_when_received=game.turn+1)
        return messages

class end_game(viewsets.ModelViewSet):
    """ show list of encryption types"""
    permission_classes = (AllowAny,)
    serializer_class = GameSerializer

    def partial_update(self, request, pk=None):
        game = get_game(self.request)
        if not game:
            return Response({'error': 'There is no game to end'},status=status.HTTP_200_OK)
        game.has_ended = True
        game.save()
        data =  {'name':game.name,
                'turn': game.turn,
                'current_time' : game.calculate_time()}
        return Response(data,status=status.HTTP_200_OK)


class category(viewsets.ModelViewSet):
    """ get list of messages"""
    permission_classes = (AllowAny,)
    serializer_class = CategorySerializer

    def get_queryset(self):
        """ list of messages """
        game_name = self.kwargs['game_name']
        game = get_game(self.request, game_name)
        if not game:
            return []
        categories = Category.objects.filter(game=game)
        return categories

    def add_category(self, request, pk=None):
        game_name = self.kwargs['game_name']
        category = self.kwargs['category']
        game = get_game(self.request, game_name)
        if not game:
            return Response({'error': 'There is no game to end'},status=status.HTTP_200_OK)
        category_serializer = CategorySerializer(data={'number': category,
                                                       'game': game}, context={'request': request})
        category_serializer.is_valid(raise_exception=True)
        serializer.save()
        data =  {'game':game.name,
                'category': category}
        return Response(data,status=status.HTTP_200_OK)

    def remove_category(self, request, pk=None):
        game_name = self.kwargs['game_name']
        category = request.POST.get('category_id', None)
        game = get_game(self.request, game_name)
        if not game:
            return Response({'error': 'There is no game to end'},status=status.HTTP_200_OK)
        categories = Category.objects.filter(game=game, number=int(category))
        for category in categories:
            category.delete()
        data =  {'game':game.name,
                'category': category}
        return Response(data,status=status.HTTP_200_OK)