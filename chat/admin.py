from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at', 'get_last_message')
    list_filter = ('created_at',)
    search_fields = ('participants__username', 'messages__content')
    date_hierarchy = 'created_at'

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Участники'

    def get_last_message(self, obj):
        if obj.last_message:
            return f"{obj.last_message.content[:50]}..."
        return "Нет сообщений"
    get_last_message.short_description = 'Последнее сообщение'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'content_preview', 'file', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'sender', 'recipient')
    search_fields = ('content', 'sender__username', 'recipient__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def content_preview(self, obj):
        return obj.content[:100] if obj.content else "Нет текста"
    content_preview.short_description = 'Содержание'
