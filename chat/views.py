from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max, F, Count
from django.core.paginator import Paginator
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

@login_required
def chat_list(request):
    """Список чатов пользователя"""
    # Получаем все чаты пользователя
    chat_rooms = ChatRoom.objects.filter(
        participants=request.user
    ).annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        ),
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')

    # Пагинация
    paginator = Paginator(chat_rooms, 20)
    page = request.GET.get('page')
    chat_rooms = paginator.get_page(page)

    return render(request, 'chat/chat_list.html', {
        'chat_rooms': chat_rooms
    })

@login_required
def chat_room(request, pk):
    """Отдельная чат-комната"""
    chat_room = get_object_or_404(ChatRoom, pk=pk)
    
    # Проверяем, является ли пользователь участником чата
    if request.user not in chat_room.participants.all():
        messages.error(request, 'У вас нет доступа к этому чату.')
        return redirect('chat_list')
    
    # Получаем сообщения
    chat_messages = chat_room.messages.select_related('sender').all()
    
    # Отмечаем сообщения как прочитанные
    chat_room.mark_messages_as_read(request.user)
    
    # Получаем собеседника
    other_participant = chat_room.participants.exclude(id=request.user.id).first()

    return render(request, 'chat/chat_room.html', {
        'chat_room': chat_room,
        'messages': chat_messages,
        'other_participant': other_participant
    })

@login_required
def send_message(request, pk):
    """Отправка сообщения"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    chat_room = get_object_or_404(ChatRoom, pk=pk)
    
    # Проверяем, является ли пользователь участником чата
    if request.user not in chat_room.participants.all():
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Получаем получателя
    recipient = chat_room.participants.exclude(id=request.user.id).first()
    
    content = request.POST.get('content', '').strip()
    file = request.FILES.get('file')

    if not content and not file:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    # Создаем сообщение
    message = Message.objects.create(
        room=chat_room,
        sender=request.user,
        recipient=recipient,
        content=content,
        file=file
    )

    # Формируем данные для ответа
    response_data = {
        'id': message.id,
        'content': message.content,
        'sender': message.sender.username,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': message.is_read
    }

    if message.file:
        response_data['file'] = {
            'url': message.file.url,
            'is_image': message.is_image,
            'extension': message.file_extension
        }

    return JsonResponse(response_data)

@login_required
def start_chat(request, username):
    """Начать новый чат с пользователем"""
    other_user = get_object_or_404(User, username=username)
    
    # Проверяем, существует ли уже чат с этим пользователем
    existing_chat = ChatRoom.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if existing_chat:
        return redirect('chat_room', pk=existing_chat.pk)

    # Создаем новую чат-комнату
    chat_room = ChatRoom.objects.create()
    chat_room.participants.add(request.user, other_user)

    return redirect('chat_room', pk=chat_room.pk)

@login_required
def mark_as_read(request, pk):
    """Отметить сообщения как прочитанные"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    chat_room = get_object_or_404(ChatRoom, pk=pk)
    
    if request.user not in chat_room.participants.all():
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Отмечаем сообщения как прочитанные
    chat_room.mark_messages_as_read(request.user)

    return JsonResponse({'status': 'success'})

@login_required
def load_more_messages(request, pk):
    """Загрузить больше сообщений"""
    chat_room = get_object_or_404(ChatRoom, pk=pk)
    
    if request.user not in chat_room.participants.all():
        return JsonResponse({'error': 'Access denied'}, status=403)

    last_message_id = request.GET.get('last_message_id')
    messages_per_page = 20

    messages_query = chat_room.messages.select_related('sender')
    
    if last_message_id:
        messages_query = messages_query.filter(id__lt=last_message_id)

    messages = messages_query.order_by('-created_at')[:messages_per_page]

    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'sender': msg.sender.username,
        'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': msg.is_read,
        'file_url': msg.file.url if msg.file else None,
        'is_image': msg.is_image if msg.file else False,
        'file_extension': msg.file_extension if msg.file else None
    } for msg in messages]

    return JsonResponse({
        'messages': messages_data,
        'has_more': len(messages) == messages_per_page
    })
