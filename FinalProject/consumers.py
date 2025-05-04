from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from RecruitHelper.models import Chat, Message, CUser
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.user = self.scope['user']

        if await self.validate_access():
            await self.accept()
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
        else:
            await self.close(code=4001)

    @property
    def room_group_name(self):
        return f'chat_{self.chat_id}'

    @database_sync_to_async
    def validate_access(self):
        if self.user.role == 'company':
            print(self.user.company, 'company')
            validated = Chat.objects.filter(
                id=self.chat_id,
                company=self.user.company
            ).exists()
            print(validated)
            return validated
        else:
            print(self.user.cuser, 'cuser')
            validated = Chat.objects.filter(
                id=self.chat_id,
                user=self.user.cuser
            ).exists()
            print(validated)
            return validated

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = await self.create_message(data['content'])
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    @database_sync_to_async
    def create_message(self, content):
        chat = Chat.objects.get(id=self.chat_id)
        message = Message.objects.create(
            user=self.user,
            content=content
        )
        message.chat.add(chat)
        return {
            'user': {
                'main_name': message.user.main_name,
            },
            'content': message.content,
            'timestamp': message.timestamp.isoformat()
        }

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))