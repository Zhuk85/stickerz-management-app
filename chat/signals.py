from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, ChatRoom

@receiver(post_save, sender=Message)
def update_chat_room_last_message(sender, instance, created, **kwargs):
    """
    Обновляет последнее сообщение в чат-комнате при создании нового сообщения
    """
    if created:
        chat_room = instance.room
        chat_room.last_message = instance
        chat_room.save(update_fields=['last_message'])

@receiver(post_save, sender=Message)
def notify_users_about_new_message(sender, instance, created, **kwargs):
    """
    Отправляет уведомление о новом сообщении
    В будущем здесь можно добавить отправку push-уведомлений,
    email-уведомлений или WebSocket-сообщений
    """
    if created:
        # Здесь будет логика отправки уведомлений
        pass
