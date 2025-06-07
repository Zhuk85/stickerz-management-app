from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Sticker, City, Category, Comment
from .forms import StickerForm, CommentForm
import os
from moviepy.editor import VideoFileClip
from PIL import Image
from datetime import datetime

def home(request):
    """Главная страница"""
    # Получаем последние стикеры
    latest_stickers = Sticker.objects.select_related('author', 'city', 'category').order_by('-created_at')[:12]
    
    # Получаем популярные города
    popular_cities = City.objects.all()[:6]
    
    # Получаем все категории
    categories = Category.objects.all()

    return render(request, 'stickers/home.html', {
        'latest_stickers': latest_stickers,
        'popular_cities': popular_cities,
        'categories': categories
    })

def sticker_list(request):
    """Список стикеров с фильтрацией и поиском"""
    stickers = Sticker.objects.select_related('author', 'city', 'category').all()
    
    # Фильтрация по городу
    city = request.GET.get('city')
    if city:
        stickers = stickers.filter(city__slug=city)
    
    # Фильтрация по категории
    category = request.GET.get('category')
    if category:
        stickers = stickers.filter(category__slug=category)
    
    # Поиск по тексту
    query = request.GET.get('q')
    if query:
        stickers = stickers.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Сортировка
    sort = request.GET.get('sort', '-created_at')
    if sort == 'popular':
        stickers = stickers.order_by('-views_count')
    elif sort == 'likes':
        stickers = stickers.order_by('-likes')
    else:
        stickers = stickers.order_by(sort)
    
    # Пагинация
    paginator = Paginator(stickers, 12)
    page = request.GET.get('page')
    stickers = paginator.get_page(page)
    
    return render(request, 'stickers/sticker_list.html', {
        'stickers': stickers,
        'cities': City.objects.all(),
        'categories': Category.objects.all()
    })

def sticker_detail(request, pk):
    """Детальная страница стикера"""
    sticker = get_object_or_404(
        Sticker.objects.select_related('author', 'city', 'category'),
        pk=pk
    )
    
    # Увеличиваем счетчик просмотров
    sticker.views_count += 1
    sticker.save()
    
    # Форма комментария
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.sticker = sticker
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('sticker_detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    return render(request, 'stickers/sticker_detail.html', {
        'sticker': sticker,
        'comment_form': comment_form
    })

@login_required
def sticker_create(request):
    """Создание нового стикера"""
    if request.method == 'POST':
        form = StickerForm(request.POST, request.FILES)
        if form.is_valid():
            sticker = form.save(commit=False)
            sticker.author = request.user
            
            # Обработка медиафайла
            if sticker.media_type == 'video':
                # Создаем превью для видео
                video = VideoFileClip(sticker.media_file.path)
                preview_path = os.path.join('media/stickers/previews/', f'{datetime.now().timestamp()}.jpg')
                video.save_frame(preview_path, t=1.0)
                sticker.preview_image = preview_path
                video.close()
            
            sticker.save()
            messages.success(request, 'Стикер успешно создан!')
            return redirect('sticker_detail', pk=sticker.pk)
    else:
        form = StickerForm()
    
    return render(request, 'stickers/sticker_form.html', {
        'form': form,
        'title': 'Создать стикер'
    })

@login_required
def sticker_edit(request, pk):
    """Редактирование стикера"""
    sticker = get_object_or_404(Sticker, pk=pk)
    
    # Проверка прав доступа
    if sticker.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования этого стикера.')
        return redirect('sticker_detail', pk=pk)
    
    if request.method == 'POST':
        form = StickerForm(request.POST, request.FILES, instance=sticker)
        if form.is_valid():
            sticker = form.save()
            messages.success(request, 'Стикер успешно обновлен!')
            return redirect('sticker_detail', pk=sticker.pk)
    else:
        form = StickerForm(instance=sticker)
    
    return render(request, 'stickers/sticker_form.html', {
        'form': form,
        'title': 'Редактировать стикер'
    })

@login_required
def sticker_delete(request, pk):
    """Удаление стикера"""
    sticker = get_object_or_404(Sticker, pk=pk)
    
    # Проверка прав доступа
    if sticker.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для удаления этого стикера.')
        return redirect('sticker_detail', pk=pk)
    
    if request.method == 'POST':
        sticker.delete()
        messages.success(request, 'Стикер успешно удален!')
        return redirect('sticker_list')
    
    return render(request, 'stickers/sticker_confirm_delete.html', {
        'sticker': sticker
    })

@login_required
def like_sticker(request, pk):
    """Лайк/анлайк стикера"""
    if request.method == 'POST':
        sticker = get_object_or_404(Sticker, pk=pk)
        
        if request.user in sticker.likes.all():
            sticker.likes.remove(request.user)
            liked = False
        else:
            sticker.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'likes_count': sticker.likes_count
        })
