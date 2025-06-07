from django.urls import path
from . import views

urlpatterns = [
    # Список чатов
    path('', views.chat_list, name='chat_list'),
    
    # Отдельная чат-комната
    path('<int:pk>/', views.chat_room, name='chat_room'),
    
    # API для работы с сообщениями
    path('<int:pk>/send/', views.send_message, name='send_message'),
    path('<int:pk>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('<int:pk>/load-more/', views.load_more_messages, name='load_more_messages'),
    
    # Создание нового чата
    path('start/<str:username>/', views.start_chat, name='start_chat'),
]
