from . import views
from django.urls import path

get_round = views.get_round.as_view({'get': 'retrieve',
                                     'patch': 'partial_update',
                                     })
end_game = views.end_game.as_view({'patch': 'partial_update'})
get_messages = views.get_messages.as_view({'get': 'list',
                                        })

urlpatterns = [
    path('get_round/', get_round),
    path('end_game/', end_game),
    path('new_game/', views.new_game.as_view({'post': 'create_game'})),
    path('next_turn/', get_round),
    path('get_messages/', get_messages),
    path('send_message/', views.new_message.as_view({'post': 'create_message'})),
    path('check_messages/', views.check_messages.as_view({'get': 'list'}))
]
