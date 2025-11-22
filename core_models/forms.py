from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label="Кто вы?",
        widget=forms.RadioSelect,
        initial='jobseeker'
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone', 'role')
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'phone': 'Телефон',
        }
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+996 (___) __-__-__'}),
        }
