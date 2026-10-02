"""
Команда для заполнения базы данных демо-данными.
Использование: python manage.py populate_demo
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import (
    SiteSettings, Skill, Project, Article, ArticleCategory,
    Experience, Education, Achievement, Comment
)
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных демо-данными'

    def handle(self, *args, **options):
        self.stdout.write('Создание демо-данных...')

        # Создание настроек сайта
        settings, created = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'deev.space',
                'site_description': 'Персональный сайт backend-разработчика',
                'owner_name': 'Деев Егор Викторович',
                'owner_title': 'Backend Developer',
                'owner_city': 'Москва',
                'owner_email': 'deev@example.com',
                'owner_phone': '+7 (999) 123-45-67',
                'owner_bio': 'Опытный backend-разработчик с более чем 3-летним стажем...',
                'telegram_url': 'https://t.me/Egor_Deev',
                'github_url': 'https://github.com/Egor-Deev',
            }
        )

        # Создание навыков
        skills_data = [
            {'name': 'Python', 'category': 'backend', 'icon': 'devicon-python-plain'},
            {'name': 'Django', 'category': 'backend', 'icon': 'devicon-django-plain'},
            {'name': 'FastAPI', 'category': 'backend', 'icon': 'fas fa-bolt'},
            {'name': 'PostgreSQL', 'category': 'database', 'icon': 'devicon-postgresql-plain'},
            {'name': 'Redis', 'category': 'database', 'icon': 'devicon-redis-plain'},
            {'name': 'Docker', 'category': 'devops', 'icon': 'devicon-docker-plain'},
            {'name': 'Git', 'category': 'devops', 'icon': 'devicon-git-plain'},
            {'name': 'Linux', 'category': 'devops', 'icon': 'devicon-linux-plain'},
            {'name': 'HTML/CSS', 'category': 'frontend', 'icon': 'devicon-html5-plain'},
            {'name': 'JavaScript', 'category': 'frontend', 'icon': 'devicon-javascript-plain'},
        ]

        for data in skills_data:
            Skill.objects.get_or_create(**data)

        # Создание проектов
        projects_data = [
            {
                'title': 'TaskMaster Pro',
                'slug': 'taskmaster-pro',
                'short_description': 'Система управления задачами с AI-рекомендациями',
                'technologies': 'Python, Django, PostgreSQL, Redis, Celery',
                'status': 'completed',
                'card_size': 'featured',
                'icon': 'fas fa-tasks',
                'is_featured': True,
            },
            {
                'title': 'DataParser',
                'slug': 'dataparser',
                'short_description': 'Высоконагруженный парсер данных с автоматизацией',
                'technologies': 'Python, Scrapy, PostgreSQL, Docker',
                'status': 'completed',
                'card_size': 'regular',
                'icon': 'fas fa-database',
            },
            {
                'title': 'API Gateway',
                'slug': 'api-gateway',
                'short_description': 'Микросервисный API Gateway с авторизацией',
                'technologies': 'Python, FastAPI, Redis, JWT',
                'status': 'in_development',
                'card_size': 'regular',
                'icon': 'fas fa-server',
            },
        ]

        for data in projects_data:
            Project.objects.get_or_create(slug=data['slug'], defaults=data)

        # Создание категорий статей
        categories_data = [
            {'name': 'Python', 'slug': 'python', 'icon': 'devicon-python-plain'},
            {'name': 'Django', 'slug': 'django', 'icon': 'devicon-django-plain'},
            {'name': 'DevOps', 'slug': 'devops', 'icon': 'fas fa-server'},
        ]

        for data in categories_data:
            ArticleCategory.objects.get_or_create(slug=data['slug'], defaults=data)

        # Создание статей
        python_cat = ArticleCategory.objects.get(slug='python')
        articles_data = [
            {
                'title': 'Асинхронное программирование в Python',
                'slug': 'async-python',
                'excerpt': 'Разбираем asyncio и современные подходы...',
                'post': '<p>Полный текст статьи об асинхронном программировании...</p>',
                'category': python_cat,
                'is_published': True,
            },
            {
                'title': 'Оптимизация Django ORM',
                'slug': 'django-orm-optimization',
                'excerpt': 'Как ускорить запросы к базе данных...',
                'post': '<p>Полный текст статьи об оптимизации Django ORM...</p>',
                'category': ArticleCategory.objects.get(slug='django'),
                'is_published': True,
            },
        ]

        for data in articles_data:
            Article.objects.get_or_create(slug=data['slug'], defaults=data)

        # Создание опыта работы
        Experience.objects.get_or_create(
            company='Tech Company',
            defaults={
                'title': 'Backend Developer',
                'start_date': date(2022, 1, 1),
                'is_current': True,
                'description': 'Разработка backend-систем на Python/Django',
            }
        )

        # Создание образования
        Education.objects.get_or_create(
            institution='Московский Политехнический Университет',
            defaults={
                'institution_short': 'МосПолитех',
                'degree': 'Информационные системы и технологии',
                'education_type': 'university',
                'start_year': 2021,
                'is_current': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('Демо-данные успешно созданы!'))