from django.db import models
from django.conf import settings
from django.urls import reverse

class ChatRoom(models.Model):
    """Модель чат-комнаты"""
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms',
        verbose_name='Участники'
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    last_message = models.ForeignKey(
        'Message',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_message_room',
        verbose_name='Последнее сообщение'
    )

    class Meta:
        verbose_name = 'Чат-комната'
        verbose_name_plural = 'Чат-комнаты'
        ordering = ['-last_message__created_at'] if last_message else ['-created_at']

    def __str__(self):
        participants = self.participants.all()
        return f'Чат между {" и ".join([str(p) for p in participants])}'

    def get_absolute_url(self):
        return reverse('chat_room', kwargs={'pk': self.pk})

    @property
    def unread_messages_count(self):
        """Возвращает количество непрочитанных сообщений"""
        return self.messages.filter(is_read=False).count()

    def mark_messages_as_read(self, user):
        """Отмечает все сообщения в комнате как прочитанные для указанного пользователя"""
        self.messages.filter(recipient=user, is_read=False).update(is_read=True)

class Message(models.Model):
    """Модель сообщения"""
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Чат-комната'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Получатель'
    )
    content = models.TextField('Текст сообщения')
    file = models.FileField(
        'Файл',
        upload_to='chat_files/',
        null=True,
        blank=True
    )
    is_read = models.BooleanField(
        'Прочитано',
        default=False
    )
    created_at = models.DateTimeField(
        'Дата отправки',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']

    def __str__(self):
        return f'Сообщение от {self.sender} для {self.recipient}'

    def save(self, *args, **kwargs):
        """Переопределяем save для обновления last_message в чат-комнате"""
        super().save(*args, **kwargs)
        self.room.last_message = self
        self.room.save()

    @property
    def file_extension(self):
        """Возвращает расширение прикрепленного файла"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None

    @property
    def is_image(self):
        """Проверяет, является ли файл изображением"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif']
        return self.file_extension in image_extensions if self.file_extension else False
