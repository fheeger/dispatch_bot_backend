from .models import Game, Channel, Message, Profile, UserGameRelation, Category
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import json
from .exception import GameRetrievalException

class MyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.game=Game.objects.create(name="Great game",
                                server_id=1241432,
                                user_id=333,
                                turn=2
                                )
        self.category=Category.objects.create(number=1,
                                              game=self.game)
        self.user=User.objects.create(username='admin',
                                      password='MyPassword')
        self.user_game=UserGameRelation.objects.create(user=self.user,
                                                       game=self.game)
        self.profile=Profile.objects.create(user=self.user,
                                            discord_id="666")
        self.channel=Channel.objects.create(name='test channel',
                                            game=self.game,
                                            channel_id=1)
        self.message=Message.objects.create(text='test message',
                                            sender='General McArthur',
                                            turn_when_sent=2,
                                            turn_when_received=3,
                                            game=self.game,
                                            channel=self.channel
                                            )
        self.approved_message=Message.objects.create(text='test message approved',
                                            sender='General McArthur',
                                            turn_when_sent=1,
                                            turn_when_received=2,
                                            game=self.game,
                                            channel=self.channel,
                                            approved=True
                                            )
        self.sent_message=Message.objects.create(text='test message sent',
                                            sender='General McArthur',
                                            turn_when_sent=1,
                                            turn_when_received=1,
                                            game=self.game,
                                            channel=self.channel,
                                            approved=True
                                            )
        self.lost_message=Message.objects.create(text='test message',
                                            sender='General McArthur',
                                            turn_when_sent=1,
                                            turn_when_received=2,
                                            game=self.game,
                                            channel=self.channel,
                                            is_lost=True
                                            )


    def test_get_round(self):
        url = '/bot/get_round/'
        ###testing for a game that exist
        self.client.force_authenticate(self.user)
        data={'server_id':self.game.server_id,
              'category_id':self.category
              }
        request = self.client.get(url, data=data)
        request_data = request.json()
        self.assertEqual(request_data,{'turn': 2, 'name': 'Great game', 'start_time': '08:00:00', 'server_id': 1241432, 'user_id': 333})

        ##testing a not existing game
        data = {'server_id': 0,
                'category_id': self.category
                }
        request = self.client.get(url, data=data)
        request_data = request.json()
        self.assertEqual(request_data['turn'], None)

    def test_next_turn(self):
        url = '/bot/next_turn/'
        ###testing for a game that exist
        self.client.force_authenticate(self.user)
        data={'server_id':self.game.server_id,
              'category_id':self.category
              }
        request = self.client.patch(url, data=data)
        request_data = request.json()
        self.assertEqual(request_data, {'current_time': '08:30:00', 'name': 'Great game', 'turn': 3})

        ##testing a not existing game
        data = {'server_id': 0,
                'category_id': self.category
                }
        request = self.client.patch(url, data=data)
        request_data = request.json()
        self.assertEqual(request_data, 'No game found')


    def test_end_game(self):
        url = '/bot/end_game/'
        ###testing for a game that exist
        self.client.force_authenticate(self.user)
        data = {'server_id': self.game.server_id,
                'category_id': self.category
                }
        request = self.client.patch(url, data=data)
        request_data = request.json()
        self.assertEqual(request_data, {'current_time': '08:15:00', 'name': 'Great game', 'turn': 2})
        self.assertEqual(Game.objects.get(id=self.game.id).has_ended, True)

        ##testing a not existing game
        data = {'server_id': 0,
                'category_id': self.category
                }
        request = self.client.patch(url, data=data)
        request_data = request.json()
        self.assertEqual(request_data, 'No game found')

    def test_new_game(self):
        url = '/bot/new_game/'
        ###testing for a game that exist
        self.client.force_authenticate(self.user)
        data = {"discord_user_id_hash": self.profile.discord_id,
                "name_game": "New_game",
                "server_id": 32,
                "channels": [{"name":"new channel","id":2}],
                "user_id": 11
                }
        request = self.client.post(url, data=json.dumps(data), content_type='application/json')
        request_data = json.loads(request.content)
        self.assertEqual(request_data, {'turn': 1, 'name': 'New_game', 'start_time': '08:00:00', 'server_id': 32, 'user_id': 11})

        ##testing game already exists
        data = {"discord_user_id_hash": self.profile.discord_id,
                "name_game": self.game.name,
                "server_id": 32,
                "channels": [{"name":"new channel","id":2}],
                "user_id": 11
                }
        request = self.client.post(url, data=data)
        request_data = json.loads(request.content)
        self.assertEqual(request_data, {'error': 'A game with the same name is already going on! Please choose another name'})

        ##testing no account for user
        data = {"discord_user_id_hash": "999",
                "name_game": "New_game",
                "server_id": 32,
                "channels": [{"name":"new channel","id":2}],
                "user_id": 11
                }
        request = self.client.post(url, data=data)
        request_data = json.loads(request.content)
        self.assertEqual(request_data, {'error': "You don't have an account"})


    def test_get_messages(self):
        url = '/bot/get_messages/'
        ###testing for a game that exist
        self.client.force_authenticate(self.user)
        data={'server_id':self.game.server_id,
              'category_id':self.category
              }
        request = self.client.get(url, data=data)
        request_data = request.json()
        self.assertEqual(len(request_data),1)
        self.assertEqual(request_data[0]['text'],self.approved_message.text)


        ##testing a not existing game
        data = {'server_id': 0,
                'category_id': self.category
                }
        with self.assertRaises(GameRetrievalException):
            self.client.get(url, data=data)
