from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from django.conf import settings
import bleach
import requests

from .models import CustomUser, Comment, ContactMessage


class SmartCaptchaField(forms.CharField):
    """Кастомное поле для Yandex SmartCaptcha."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', True)
        kwargs.setdefault('widget', forms.HiddenInput(attrs={'id': 'smart-captcha-token'}))
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        if not value:
            raise forms.ValidationError('Пожалуйста, пройдите проверку капчи')

        # Валидация токена на сервере Yandex
        if not self._verify_captcha(value):
            raise forms.ValidationError('Проверка капчи не пройдена. Попробуйте снова.')

    def _verify_captcha(self, token):
        """Проверка токена на сервере Yandex SmartCaptcha."""
        try:
            response = requests.post(
                'https://smartcaptcha.yandexcloud.net/validate',
                data={
                    'secret': settings.SMARTCAPTCHA_SERVER_KEY,
                    'token': token,
                },
                timeout=5
            )

            # Рекомендация документации: при ошибке HTTP считать проверку успешной
            if response.status_code != 200:
                return True

            result = response.json()
            return result.get('status') == 'ok'

        except requests.RequestException:
            # При сетевой ошибке пропускаем, чтобы не блокировать пользователей
            return True


class SmartCaptchaWidget(forms.Widget):
    """Виджет для отображения Yandex SmartCaptcha."""

    template_name = 'widgets/smartcaptcha.html'

    def __init__(self, attrs=None):
        default_attrs = {'class': 'smart-captcha-container'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['client_key'] = settings.SMARTCAPTCHA_CLIENT_KEY
        return context


class RegisterForm(forms.ModelForm):
    """Форма регистрации пользователя."""
    username = forms.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Имя пользователя может содержать только латинские буквы, цифры и подчёркивания'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя (латиница)',
            'autocomplete': 'username'
        }),
        label='Имя пользователя'
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (необязательно)',
            'autocomplete': 'email'
        }),
        label='Email'
    )

    password = forms.CharField(
        min_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль (минимум 4 символа)',
            'autocomplete': 'new-password'
        }),
        label='Пароль'
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль',
            'autocomplete': 'new-password'
        }),
        label='Подтверждение пароля'
    )

    captcha = SmartCaptchaField(label='')

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_verified = True
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Форма авторизации пользователя."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
            'autocomplete': 'username'
        }),
        label='Имя пользователя'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
            'autocomplete': 'current-password'
        }),
        label='Пароль'
    )

    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Запомнить меня'
    )

    error_messages = {
        'invalid_login': 'Неверное имя пользователя или пароль',
        'inactive': 'Этот аккаунт деактивирован',
    }


class CommentForm(forms.ModelForm):
    """Форма добавления комментария."""
    content = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Напишите комментарий...',
            'rows': 3
        }),
        label=''
    )

    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a', 'code', 'pre']
        allowed_attrs = {'a': ['href', 'title', 'rel']}
        content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
        content = bleach.linkify(content)
        return content


class ContactForm(forms.ModelForm):
    """Форма обратной связи."""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        }),
        label='Имя'
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email для ответа'
        }),
        label='Email'
    )

    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Тема сообщения'
        }),
        label='Тема'
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Текст сообщения',
            'rows': 5
        }),
        label='Сообщение'
    )

    captcha = SmartCaptchaField(label='')

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def clean_message(self):
        message = self.cleaned_data.get('message')
        message = bleach.clean(message, tags=[], strip=True)
        return message