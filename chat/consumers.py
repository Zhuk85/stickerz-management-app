import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Установка WebSocket-соединения"""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Проверяем доступ пользователя к чату
        if not await self.has_chat_access():
            await self.close()
            return

        # Добавляем пользователя в группу чата
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Отправляем статус "онлайн"
        await self.update_user_status(True)

    async def disconnect(self, close_code):
        """Закрытие WebSocket-соединения"""
        # Отправляем статус "оффлайн"
        await self.update_user_status(False)

        # Удаляем пользователя из группы чата
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Получение сообщения от клиента"""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'message':
            # Обработка нового сообщения
            message = data.get('message')
            if message:
                # Сохраняем сообщение в базу данных
                saved_message = await self.save_message(message)
                
                # Отправляем сообщение всем участникам чата
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': saved_message.id,
                            'content': saved_message.content,
                            'sender': self.user.username,
                            'created_at': saved_message.created_at.isoformat(),
                            'is_read': False
                        }
                    }
                )
        
        elif message_type == 'typing':
            # Отправляем уведомление о наборе текста
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'user': self.user.username
                }
            )
        
        elif message_type == 'read':
            # Отмечаем сообщения как прочитанные
            message_ids = data.get('message_ids', [])
            if message_ids:
                await self.mark_messages_as_read(message_ids)
                
                # Отправляем уведомление о прочтении
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'messages_read',
                        'message_ids': message_ids,
                        'reader': self.user.username
                    }
                )

    async def chat_message(self, event):
        """Отправка сообщения клиенту"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))

    async def user_typing(self, event):
        """Отправка уведомления о наборе текста"""
        if event['user'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user': event['user']
            }))

    async def messages_read(self, event):
        """Отправка уведомления о прочтении сообщений"""
        await self.send(text_data=json.dumps({
            'type': 'read',
            'message_ids': event['message_ids'],
            'reader': event['reader']
        }))

    async def user_status(self, event):
        """Отправка уведомления об изменении статуса пользователя"""
        await self.send(text_data=json.dumps({
            'type': 'status',
            'user': event['user'],
            'status': event['status']
        }))

    @database_sync_to_async
    def has_chat_access(self):
        """Проверка доступа пользователя к чату"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            return self.user in chat_room.participants.all()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        """Сохранение сообщения в базу данных"""
        chat_room = ChatRoom.objects.get(id=self.room_id)
        recipient = chat_room.participants.exclude(id=self.user.id).first()
        
        return Message.objects.create(
            room=chat_room,
            sender=self.user,
            recipient=recipient,
            content=content
        )

    @database_sync_to_async
    def mark_messages_as_read(self, message_ids):
        """Отметка сообщений как прочитанных"""
        Message.objects.filter(
            id__in=message_ids,
            recipient=self.user,
            is_read=False
        ).update(is_read=True)

    async def update_user_status(self, is_online):
        """Обновление статуса пользователя"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user': self.user.username,
                'status': 'online' if is_online else 'offline'
            }
        )
