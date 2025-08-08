from rest_framework import serializers
from .models import VideoChatUser, VideoChatRoom, Signal

class VideoChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoChatUser
        fields = '__all__'

class VideoChatRoomSerializer(serializers.ModelSerializer):
    participants = VideoChatUserSerializer(many=True, read_only=True)

    class Meta:
        model = VideoChatRoom
        fields = '__all__'

class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = '__all__'