from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class User(AbstractUser):
    """Расширенная модель пользователя"""
    email = models.EmailField('Email', unique=True)
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        'О себе',
        max_length=500,
        blank=True
    )
    location = models.CharField(
        'Местоположение',
        max_length=100,
        blank=True
    )
    website = models.URLField(
        'Веб-сайт',
        blank=True
    )
    date_modified = models.DateTimeField(
        'Дата изменения',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})

    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        full_name = super().get_full_name()
        return full_name if full_name else self.username

    @property
    def avatar_url(self):
        """Возвращает URL аватара или URL аватара по умолчанию"""
        if self.avatar:
            return self.avatar.url
        return '/static/img/default-avatar.png'

    @property
    def stickers_count(self):
        """Возвращает количество стикеров пользователя"""
        return self.sticker_set.count()

    @property
    def likes_given_count(self):
        """Возвращает количество лайков, поставленных пользователем"""
        return self.liked_stickers.count()

    @property
    def likes_received_count(self):
        """Возвращает количество лайков, полученных пользователем"""
        return sum(sticker.likes.count() for sticker in self.sticker_set.all())

    def save(self, *args, **kwargs):
        """Переопределяем метод save для обработки email"""
        self.email = self.email.lower()
        super().save(*args, **kwargs)
