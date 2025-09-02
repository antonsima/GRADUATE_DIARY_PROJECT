from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        label=_('First Name'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('First Name')})
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Last Name')})
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Password')})
    )
    password2 = forms.CharField(
        label=_('Password Confirmation'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm Password')})
    )

    avatar = forms.ImageField(
        label=_('Avatar'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'avatar')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Проверка размера файла (максимум 2MB)
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError(_('Размер файла не должен превышать 2MB'))

            # Проверка типа файла
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            import os
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(_('Поддерживаются только JPEG, PNG и GIF файлы'))

        return avatar

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Password')})
    )