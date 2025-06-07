from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации нового пользователя"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

class ProfileUpdateForm(forms.ModelForm):
    """Форма для обновления профиля пользователя"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

class AvatarUpdateForm(forms.ModelForm):
    """Форма для обновления аватара пользователя"""
    class Meta:
        model = User
        fields = ('avatar',)
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Проверяем размер файла (максимум 2MB)
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 2MB')
            
            # Проверяем расширение файла
            allowed_extensions = ['jpg', 'jpeg', 'png']
            ext = avatar.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Разрешены только форматы: {", ".join(allowed_extensions)}'
                )
        return avatar
