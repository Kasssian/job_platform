import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Message
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            await self.accept()

        self.personal_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.personal_group, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.personal_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        recipient_id = data['recipient_id']
        text = data['text']

        message = await sync_to_async(Message.objects.create)(
            sender=self.user,
            recipient_id=recipient_id,
            text=text
        )

        await self.channel_layer.group_send(
            f"user_{self.user.id}",
            {"type": "chat_message", "message": MessageSerializer(message).data}
        )
        await self.channel_layer.group_send(
            f"user_{recipient_id}",
            {"type": "chat_message", "message": MessageSerializer(message).data}
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
