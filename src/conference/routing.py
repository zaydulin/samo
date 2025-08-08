from django.urls import path, re_path
from .consumers import ChatConsumer ,VideoChatConsumer,RoomControlConsumer, ParticipantConsumer , NotAddedConsumer, UserRedirectConsumer


websocket_urlpatterns = [
    path('video/<slug:slug>/', VideoChatConsumer.as_asgi()),
    path('chat/<slug:room_name>/', ChatConsumer.as_asgi()),
    path('room_control/<slug:slug>/', RoomControlConsumer.as_asgi()),
    path('participants/<slug:slug>/', ParticipantConsumer.as_asgi()),
    path('notadded/<slug:slug>/', NotAddedConsumer.as_asgi()),
    path('user_redirect/', UserRedirectConsumer.as_asgi()),
]