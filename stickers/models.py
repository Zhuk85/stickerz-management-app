from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

class City(models.Model):
    """Модель города"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='cities/', blank=True)
    coordinates = models.CharField('Координаты', max_length=50, help_text='Формат: широта,долгота')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('city_detail', kwargs={'slug': self.slug})

class Category(models.Model):
    """Модель категории стикеров"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    icon = models.CharField('Иконка', max_length=50, help_text='Название иконки из Font Awesome', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Sticker(models.Model):
    """Модель стикера"""
    MEDIA_TYPES = (
        ('photo', 'Фото'),
        ('video', 'Видео'),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    media_type = models.CharField('Тип медиа', max_length=5, choices=MEDIA_TYPES)
    media_file = models.FileField('Медиафайл', upload_to='stickers/')
    preview_image = models.ImageField(
        'Превью',
        upload_to='stickers/previews/',
        blank=True,
        help_text='Автоматически создается для видео'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name='Город'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    location_coordinates = models.CharField(
        'Координаты места',
        max_length=50,
        help_text='Формат: широта,долгота'
    )
    navigation_link = models.URLField(
        'Ссылка на навигацию',
        blank=True,
        help_text='Ссылка на Google Maps или 2GIS'
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_stickers',
        verbose_name='Лайки',
        blank=True
    )
    views_count = models.PositiveIntegerField('Просмотры', default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Стикер'
        verbose_name_plural = 'Стикеры'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('sticker_detail', kwargs={'pk': self.pk})

    @property
    def likes_count(self):
        return self.likes.count()

class Comment(models.Model):
    """Модель комментария к стикеру"""
    sticker = models.ForeignKey(
        Sticker,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Стикер'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий от {self.author} к {self.sticker}'
