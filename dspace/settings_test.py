"""Настройки для тестов: боевой режим (DEBUG=False), но без SSL-редиректа и внешних сервисов."""
import os

os.environ.setdefault('DJANGO_SECRET_KEY', 'test-secret-key-not-for-production')
os.environ.setdefault('DJANGO_DEBUG', 'False')
os.environ.setdefault('DJANGO_SECURE_SSL_REDIRECT', 'False')
os.environ.setdefault('DJANGO_ALLOWED_HOSTS', 'testserver,localhost')

from .settings import *  # noqa: E402,F403

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
