from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from RecruitHelper.models import Chat, Message, CUser
import json

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer для обработки чатов.
    """
    async def connect(self):
        """
        Устанавливает WebSocket соединение.

        Проверяет доступ пользователя к чату и принимает соединение.
        """
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
        """
        Формирует имя группы канала для чата.

        :return: Имя группы канала.
        """
        return f'chat_{self.chat_id}'

    @database_sync_to_async
    def validate_access(self):
        """
        Проверяет право доступа текущего пользователя к чату.

        :return: True, если доступ разрешен, False в противном случае.
        """
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
        """
        Отключает WebSocket соединение.

        Удаляет канал из группы канала чата.
        :param close_code: Код закрытия соединения.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Обрабатывает полученные по WebSocket данные.

        Создает новое сообщение и отправляет его в группу канала чата.
        :param text_data: Полученные данные в текстовом формате (ожидается JSON).
        """
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
        """
        Создает новое сообщение в базе данных и связывает его с текущим чатом.

        :param content: Содержимое сообщения.
        :return: Словарь с данными созданного сообщения для отправки клиентам.
        """
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
        """
        Отправляет сообщение клиенту через WebSocket.

        :param event: Словарь с данными сообщения (ожидается ключ 'message').
        """
        await self.send(text_data=json.dumps(event['message']))