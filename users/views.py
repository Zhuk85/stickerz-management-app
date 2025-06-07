from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, ProfileUpdateForm, AvatarUpdateForm
from .models import User
from stickers.models import Sticker

def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

@login_required
def profile(request):
    """Профиль текущего пользователя"""
    # Получаем стикеры пользователя
    stickers = Sticker.objects.filter(author=request.user).order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(stickers, 9)  # 9 стикеров на страницу
    page = request.GET.get('page')
    stickers = paginator.get_page(page)
    
    return render(request, 'users/profile.html', {
        'user': request.user,
        'stickers': stickers,
        'title': 'Мой профиль'
    })

@login_required
def profile_edit(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=request.user)
        avatar_form = AvatarUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        
        if profile_form.is_valid() and avatar_form.is_valid():
            profile_form.save()
            avatar_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        avatar_form = AvatarUpdateForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {
        'profile_form': profile_form,
        'avatar_form': avatar_form,
        'title': 'Редактирование профиля'
    })

def profile_detail(request, username):
    """Просмотр профиля пользователя"""
    user = get_object_or_404(User, username=username)
    
    # Получаем стикеры пользователя
    stickers = Sticker.objects.filter(author=user).order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(stickers, 9)  # 9 стикеров на страницу
    page = request.GET.get('page')
    stickers = paginator.get_page(page)
    
    # Статистика
    stats = {
        'stickers_count': user.stickers_count,
        'likes_given': user.likes_given_count,
        'likes_received': user.likes_received_count
    }
    
    return render(request, 'users/profile_detail.html', {
        'profile_user': user,
        'stickers': stickers,
        'stats': stats,
        'title': f'Профиль {user.username}'
    })
