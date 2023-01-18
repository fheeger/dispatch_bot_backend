from rest_framework import viewsets, status
from rest_framework.permissions import  AllowAny
from .models import Message, Game, Category, Channel, Profile
from .serializers import GameSerializer, ChannelSerializer, MessageSerializer, CategorySerializer, UserSerializer, \
    ProfileSerializer, UserGameRelationSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .exception import GameRetrievalException
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

def get_game(request, game_name=None):
    body=request.data   ## test case with json.dumps
    if len(body)==0:
        body=getattr(request, request.method)   ##normal case
    server_id = body.get('server_id', None)
    category_id = body.get('category_id', None)
    if server_id is not None:
        games = Game.objects.filter(has_ended=False, server_id=server_id)
    else:
        games = Game.objects.filter(has_ended=False)
    if game_name:
        games = games.filter(name=game_name)
    if len(games) == 0:
        raise GameRetrievalException("No game found", status.HTTP_404_NOT_FOUND)
    elif len(games) == 1:
        return games.latest('id')
    else:
        for game in games:
            if category_id and int(category_id) in list(game.get_categories()):
                return game
        raise GameRetrievalException("Can not decide which game you want", status.HTTP_400_BAD_REQUEST)

class get_round(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = GameSerializer

    def get_object(self):
        try:
            return get_game(self.request)
        except Exception:
            return None

    def partial_update(self, request, pk=None):
        try:
            game = get_game(self.request)
        except GameRetrievalException as e:
            return Response(e.message, status=e.status)
        if not game:
            return Response({'error': 'There is no game'}, status=status.HTTP_404_NOT_FOUND)
        game.turn += 1
        game.save()
        data = {'name': game.name,
                'turn': game.turn,
                'current_time': game.calculate_time()}
        for message in Message.objects.filter(approved=False, turn_when_received=game.turn-1):
            message.set_turn(game.turn+1)
        return Response(data, status=status.HTTP_200_OK)


class new_game(viewsets.ModelViewSet):
    """ create a new game"""
    permission_classes = (AllowAny,)
    serializer_class = GameSerializer

    def create_game(self, request, *args, **kwargs):
        """ create a new game and new channels """
        if len(Profile.objects.filter(discord_id=request.data['discord_user_id_hash'])) == 0:
            return Response({'error': "You don't have an account"}, status=status.HTTP_403_FORBIDDEN)
        if len(Game.objects.filter(has_ended=False, name=request.data['name_game'])) >= 1:
            return Response({'error': 'A game with the same name is already going on! Please choose another name'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = GameSerializer(data={'name':request.data['name_game'],
                                          'server_id': request.data['server_id'],
                                          'user_id' : request.data['user_id']}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        user_game = UserGameRelationSerializer(data={'user':Profile.objects.get(discord_id=request.data['discord_user_id_hash']).user.id,
                                                     'game': game.id}, context={'request': request})
        user_game.is_valid(raise_exception=True)
        user_game.save()
        for channel in request.data['channels']:
            channel_serializer=ChannelSerializer(data={'name':channel['name'], 'channel_id': channel['id'], 'game':game.id}, context={'request': request})
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
        try:
            game = get_game(self.request)
        except GameRetrievalException as e:
            return Response(e.message, status=e.status)
        data = request.data.copy()
        data["turn_when_sent"] = game.turn
        data["turn_when_received"] = game.turn+1
        data["game"] = game.id
        serializer = MessageSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

class check_messages(viewsets.ModelViewSet):
    """ get list of messages"""
    permission_classes = (AllowAny,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        """ list of messages for the next turn that was not approved yet"""
        try:
            game = get_game(self.request)
        except GameRetrievalException as e:
            raise ValidationError(detail={"message": e.message}, code=e.status)
        messages = Message.objects.filter(game=game, approved=False, turn_when_received=game.turn+1)
        return messages

class end_game(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = GameSerializer

    def partial_update(self, request, pk=None):
        try:
            game = get_game(self.request)
        except GameRetrievalException as e:
            return Response(e.message, status=e.status)
        if not game:
            return Response({'error': 'There is no game to end'}, status=status.HTTP_404_NOT_FOUND)
        game.has_ended = True
        game.save()
        data = {'name': game.name,
                'turn': game.turn,
                'current_time': game.calculate_time()}
        return Response(data, status=status.HTTP_200_OK)


class category(viewsets.ModelViewSet):
    """ get list of categories"""
    permission_classes = (AllowAny,)
    serializer_class = CategorySerializer

    def get_queryset(self):
        """ list of messages """
        game_name = self.kwargs['game_name']
        try:
            game = get_game(self.request, game_name)
        except GameRetrievalException as e:
            raise NotFound(detail={"message": e.message}, code=e.status)
        categories = Category.objects.filter(game=game)
        return categories

    def add_category(self, request, game_name):
        categories = request.data['category']
        try:
            game = get_game(self.request, game_name)
        except GameRetrievalException as e:
            return Response(e.message, status=e.status)
        existing_categories = game.get_categories()
        for category in categories:
            if category not in existing_categories:
                category_serializer = CategorySerializer(data={'number': category,
                                                               'game': game.id}, context={'request': request})
                category_serializer.is_valid(raise_exception=True)
                category_serializer.save()
        data =  {'game':game.name,
                'categories': categories}
        return Response(data,status=status.HTTP_200_OK)

    def remove_category(self, request, game_name):
        categories = request.data['category']
        try:
            game = get_game(self.request, game_name)
        except GameRetrievalException as e:
            return Response(e.message, status=e.status)
        if not game:
            return Response({'error': 'There is no game with this name : {}'.format(game_name)},status=status.HTTP_200_OK)
        existing_categories = game.get_categories()
        for category in categories:
            if category in existing_categories:
                Category.objects.get(game=game, number=category).delete()
        data =  {'game':game.name,
                'category': categories}
        return Response(data,status=status.HTTP_200_OK)

class channel(viewsets.ModelViewSet):
    """ get list of channels"""
    permission_classes = (AllowAny,)
    serializer_class = ChannelSerializer

    def get_queryset(self):
        """ list of channels """
        try:
            game = get_game(self.request)
        except GameRetrievalException as e:
            raise ValidationError(detail={"message": e.message}, code=e.status)
        channels = Channel.objects.filter(game=game)
        return channels

    def update_channels(self, request):
        channels = request.data['channels']
        try:
            game = get_game(self.request)
        except GameRetrievalException as e:
            return Response(e.message, status=e.status)
        existing_channels = game.get_channels()
        for cId, cName in channels.items():
            if int(cId) not in existing_channels:
                channel_serializer = ChannelSerializer(
                    data={
                        'channel_id': cId,
                        'name': cName,
                        'game': game.id
                    },
                    context={
                        'request': request
                    }
                )
                channel_serializer.is_valid(raise_exception=True)
                channel_serializer.save()
            else:
                channel_to_update = Channel.objects.get(channel_id=cId)
                channel_to_update.name = cName
                channel_to_update.save()
        data = {'game': game.name,
                'channels': channels}
        return Response(data, status=status.HTTP_200_OK)

    def remove_channels(self, request):
        channels = request.data['channels']
        try:
            game = get_game(self.request)
        except GameRetrievalException as e:
            return Response(e.message, status=e.status)
        if not game:
            return Response({'error': 'There is no game'}, status=status.HTTP_200_OK)
        existing_channels = game.get_channels()
        for channel in channels:
            if channel in existing_channels:
                Channel.objects.get(game=game, channel_id=channel).delete()
        data = {'game': game.name,
                'channels': channels}
        return Response(data,status=status.HTTP_200_OK)

class new_user(viewsets.ModelViewSet):
    """ create user"""
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create_user(self, request, *args, **kwargs):
        """ create a new user """
        if len(User.objects.filter(username=request.data['username'])) >= 1:
            return Response('An user with the username {} already exists'.format(request.data['username']), status=status.HTTP_406_NOT_ACCEPTABLE)
        if len(Profile.objects.filter(discord_id=request.data['discord_user_id_hash'])) >= 1:
            return Response('An user already exists for your discord user ID', status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = UserSerializer(data={'username': request.data['username'],
                                          'is_staff': True}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        password = User.objects.make_random_password(length=10,
                                                     allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        user.set_password(password)
        for perm in Permission.objects.all():
            if 'user' in perm.name and ('Can view' in perm.name or 'Can change' in perm.name):
                user.user_permissions.add(perm)
            elif 'message' in perm.name or 'game' in perm.name:
                user.user_permissions.add(perm)
        user = serializer.save()
        profile_serializer=ProfileSerializer(data={'discord_id':request.data['discord_user_id_hash'],
                                                   'user': user.id}, context={'request': request})
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()
        return Response({**serializer.data, **{'password':password}}, status=201)