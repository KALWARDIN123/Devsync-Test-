"""
WebSocket consumer for chat functionality.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def chat_message(self, event):
        """
        Receive message from room group.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp'],
        })) 