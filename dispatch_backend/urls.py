from . import views
from django.urls import path

urlpatterns = [
    path('get_round/', views.get_round.as_view({'get': 'retrieve'})),
    path('end_game/', views.end_game.as_view({'patch': 'partial_update'})),
    path('new_game/', views.new_game.as_view({'post': 'create_game'})),
    path('next_turn/', views.get_round.as_view({'patch': 'partial_update'})),
    path('get_messages/', views.get_messages.as_view({'get': 'list'})),
    path('send_message/', views.new_message.as_view({'post': 'create_message'})),
    path('check_messages/', views.check_messages.as_view({'get': 'list'})),
    path('add_category/<str:game_name>/', views.category.as_view({'patch': 'add_category'})),
    path('remove_category/<str:game_name>/', views.category.as_view({'patch': 'remove_category'})),
    path('get_categories/<str:game_name>/', views.category.as_view({'get': 'list'})),
    path('update_channels/', views.channel.as_view({'patch': 'update_channels'})),
    path('remove_channels/', views.channel.as_view({'patch': 'remove_channels'})),
    path('get_channels/', views.channel.as_view({'get': 'list'})),
    path('new_user/', views.new_user.as_view({'post': 'create_user'})),
]
