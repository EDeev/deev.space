import math

from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Получение значения из словаря по ключу."""
    return dictionary.get(key)


@register.filter
def split(value, separator=','):
    """Разделение строки на список."""
    if not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]


@register.filter
def first_letter(value):
    """Получение первой буквы строки."""
    if value:
        return value[0].upper()
    return ''


@register.filter
def tech_icon(tech_name):
    """Возвращает CSS класс иконки для технологии."""
    icons = {
        'python': 'devicon-python-plain',
        'django': 'devicon-django-plain',
        'fastapi': 'devicon-fastapi-plain',
        'flask': 'devicon-flask-original',
        'postgresql': 'devicon-postgresql-plain',
        'sqlite': 'devicon-sqlite-plain',
        'mysql': 'devicon-mysql-plain',
        'mongodb': 'devicon-mongodb-plain',
        'redis': 'devicon-redis-plain',
        'docker': 'devicon-docker-plain',
        'kubernetes': 'devicon-kubernetes-plain',
        'nginx': 'devicon-nginx-original',
        'git': 'devicon-git-plain',
        'github': 'fab fa-github',
        'gitlab': 'devicon-gitlab-plain',
        'linux': 'devicon-linux-plain',
        'bash': 'devicon-bash-plain',
        'html': 'devicon-html5-plain',
        'html5': 'devicon-html5-plain',
        'css': 'devicon-css3-plain',
        'css3': 'devicon-css3-plain',
        'javascript': 'devicon-javascript-plain',
        'js': 'devicon-javascript-plain',
        'typescript': 'devicon-typescript-plain',
        'react': 'devicon-react-original',
        'vue': 'devicon-vuejs-plain',
        'nodejs': 'devicon-nodejs-plain',
        'bootstrap': 'devicon-bootstrap-plain',
        'tailwind': 'devicon-tailwindcss-plain',
        'figma': 'devicon-figma-plain',
        'c': 'devicon-c-plain',
        'c++': 'devicon-cplusplus-plain',
        'cpp': 'devicon-cplusplus-plain',
        'java': 'devicon-java-plain',
        'rust': 'devicon-rust-plain',
        'go': 'devicon-go-plain',
        'qt': 'devicon-qt-original',
        'pyqt': 'devicon-qt-original',
        'asyncio': 'fas fa-bolt',
        'aiogram': 'fab fa-telegram',
        'telegram': 'fab fa-telegram',
        'request': 'fas fa-globe',
        'requests': 'fas fa-globe',
        'pandas': 'devicon-pandas-original',
        'numpy': 'devicon-numpy-original',
        'gtts': 'fas fa-microphone',
        'psycopg2': 'devicon-postgresql-plain',
        'chroma': 'fas fa-database',
        'flowise': 'fas fa-robot',
        'winscp': 'fas fa-server',
    }

    tech_lower = tech_name.lower().strip()
    return icons.get(tech_lower, 'fas fa-code')


@register.filter
def status_class(status):
    """Возвращает CSS класс для статуса проекта."""
    classes = {
        'completed': 'completed',
        'in_development': 'beta',
        'beta': 'beta',
    }
    return classes.get(status, 'beta')


@register.filter
def status_label(status):
    """Возвращает текстовую метку для статуса."""
    labels = {
        'completed': 'Релиз',
        'in_development': 'В разработке',
        'beta': 'Бета',
    }
    return labels.get(status, status)


@register.simple_tag
def render_tech_badge(tech_name):
    """Рендерит HTML для бейджа технологии."""
    icon_class = tech_icon(tech_name)
    return format_html('<span class="tech-badge"><i class="{}"></i> {}</span>', icon_class, tech_name)


@register.filter
def linebreaks_list(value):
    """Преобразует текст с переносами строк в список."""
    if not value:
        return []
    return [line.strip() for line in value.split('\n') if line.strip()]


@register.filter
def reading_time(text, words_per_minute=200):
    """
    Рассчитывает время чтения текста в минутах
    """
    if not text:
        return 0

    # Подсчет слов (простой способ)
    word_count = len(text.split())

    # Расчет минут с округлением вверх
    minutes = math.ceil(word_count / words_per_minute)
    return max(1, minutes)  # минимум 1 минута

@register.filter
def ru_plural(value, forms):
    """Склонение по числу: {{ n|ru_plural:"проект,проекта,проектов" }}."""
    one, few, many = [f.strip() for f in forms.split(',')]
    n = abs(int(value)) % 100
    if 11 <= n <= 14:
        return many
    n %= 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return few
    return many
