from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stickers/', views.sticker_list, name='sticker_list'),
    path('stickers/<int:pk>/', views.sticker_detail, name='sticker_detail'),
    path('stickers/create/', views.sticker_create, name='sticker_create'),
    path('stickers/<int:pk>/edit/', views.sticker_edit, name='sticker_edit'),
    path('stickers/<int:pk>/delete/', views.sticker_delete, name='sticker_delete'),
]
