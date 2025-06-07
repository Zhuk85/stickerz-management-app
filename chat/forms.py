from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    """Форма для отправки сообщения"""
    file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf,.doc,.docx,.txt'
        })
    )

    class Meta:
        model = Message
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control message-textarea',
                'placeholder': 'Введите сообщение...',
                'rows': '1'
            })
        }

    def clean_file(self):
        """Валидация загружаемого файла"""
        file = self.cleaned_data.get('file')
        if file:
            # Проверяем размер файла (максимум 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    'Размер файла не должен превышать 10MB'
                )
            
            # Проверяем расширение файла
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Разрешены только форматы: {", ".join(allowed_extensions)}'
                )
        return file

    def clean(self):
        """Проверяем, что сообщение не пустое"""
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        file = cleaned_data.get('file')

        if not content and not file:
            raise forms.ValidationError(
                'Сообщение должно содержать текст или файл'
            )

        return cleaned_data
