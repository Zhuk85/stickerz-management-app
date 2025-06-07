from django import forms
from .models import Sticker, Comment

class StickerForm(forms.ModelForm):
    """Форма для создания и редактирования стикера"""
    
    class Meta:
        model = Sticker
        fields = [
            'title',
            'description',
            'media_type',
            'media_file',
            'city',
            'category',
            'location_coordinates',
            'navigation_link'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите ваш стикер',
                'rows': 4
            }),
            'media_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'media_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'city': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location_coordinates': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 55.7558,37.6173'
            }),
            'navigation_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ссылка на карту'
            })
        }

    def clean_media_file(self):
        """Валидация медиафайла"""
        media_file = self.cleaned_data.get('media_file')
        media_type = self.cleaned_data.get('media_type')

        if not media_file:
            raise forms.ValidationError('Загрузите файл')

        # Проверяем расширение файла
        file_extension = media_file.name.split('.')[-1].lower()
        
        if media_type == 'photo':
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    'Для фото допустимы форматы: ' + ', '.join(allowed_extensions)
                )
        elif media_type == 'video':
            allowed_extensions = ['mp4', 'mov', 'avi']
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    'Для видео допустимы форматы: ' + ', '.join(allowed_extensions)
                )

        # Проверяем размер файла (максимум 10MB)
        if media_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError('Размер файла не должен превышать 10MB')

        return media_file

    def clean_location_coordinates(self):
        """Валидация координат"""
        coords = self.cleaned_data.get('location_coordinates')
        
        if not coords:
            raise forms.ValidationError('Укажите координаты места')

        try:
            lat, lon = map(float, coords.split(','))
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise forms.ValidationError('Некорректные координаты')
        except ValueError:
            raise forms.ValidationError(
                'Координаты должны быть в формате: широта,долгота'
            )

        return coords

class CommentForm(forms.ModelForm):
    """Форма для создания комментария"""
    
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Оставьте комментарий...',
                'rows': 3
            })
        }

    def clean_text(self):
        """Валидация текста комментария"""
        text = self.cleaned_data.get('text')
        
        if not text.strip():
            raise forms.ValidationError('Комментарий не может быть пустым')
        
        if len(text) > 1000:
            raise forms.ValidationError(
                'Комментарий не должен превышать 1000 символов'
            )
        
        return text
