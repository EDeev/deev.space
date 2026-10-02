from datetime import date

from django.core.management.base import BaseCommand

from main.models import Article, Category, Education, Experience, Project, SiteSettings, Skill


class Command(BaseCommand):
    help = 'Загрузка начальных данных из резюме Деева Е.В.'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка начальных данных...\n')

        self.load_site_settings()
        self.load_skills()
        self.load_experiences()
        self.load_educations()
        self.load_projects()
        self.load_categories()
        self.load_achievements()

        self.stdout.write(self.style.SUCCESS('\n✓ Все данные успешно загружены!'))

    def load_site_settings(self):
        self.stdout.write('  → Настройки сайта...')

        settings, created = SiteSettings.objects.get_or_create(pk=1)
        settings.site_name = 'deev.space'
        settings.site_description = 'Персональный сайт backend-разработчика. Портфолио проектов, технический блог и контактная информация.'
        settings.owner_name = 'Деев Егор Викторович'
        settings.owner_title = 'Backend Developer'
        settings.owner_bio = '''Опытный разработчик с более чем 3-летним стажем программирования. Начинал профессиональный путь с обучения в Яндекс Лицее, что заложило фундамент для дальнейшего роста. Обладаю подтверждённым опытом руководства командой разработки и управления полным циклом проектов — от концепции до реализации.

Специализируюсь на создании backend-решений, парсинге данных, автоматизации процессов и интеграции AI-компонентов. Отличаюсь аналитическим складом ума, нацелен на поиск и эффективное решение сложных, нестандартных задач.'''
        settings.owner_email = 'egor@deev.space'
        settings.owner_phone = '+7 (999) 373-77-37'
        settings.owner_city = 'Москва'
        settings.telegram_url = 'https://t.me/Egor_Deev'
        settings.github_url = 'https://github.com/EDeev'
        settings.save()

        self.stdout.write(self.style.SUCCESS(' OK'))

    def load_skills(self):
        self.stdout.write('  → Навыки...')

        skills_data = [
            # Backend
            ('Python', 'backend', 'devicon-python-plain', 1),
            ('C', 'backend', 'devicon-c-plain', 2),
            ('C++', 'backend', 'devicon-cplusplus-plain', 3),
            # Frontend
            ('HTML / CSS', 'frontend', 'devicon-html5-plain', 1),
            ('Bootstrap', 'frontend', 'devicon-bootstrap-plain', 2),
            ('Figma', 'frontend', 'devicon-figma-plain', 3),
            # DevOps
            ('Nginx', 'devops', 'devicon-nginx-original', 1),
            ('Docker', 'devops', 'devicon-docker-plain', 2),
            ('Kubernetes', 'devops', 'devicon-kubernetes-plain', 3),
            ('GitLab', 'devops', 'devicon-gitlab-plain', 4),
            ('Bash', 'devops', 'devicon-bash-plain', 5),
            # Database
            ('PostgreSQL', 'database', 'devicon-postgresql-plain', 1),
            ('SQLite', 'database', 'devicon-sqlite-plain', 2),
            ('Chroma', 'database', 'fas fa-database', 3),
            # Tools
            ('Git', 'tools', 'devicon-git-plain', 1),
            ('WinSCP', 'tools', 'fas fa-server', 2),
            ('QT', 'tools', 'devicon-qt-original', 3),
            ('Django', 'tools', 'devicon-django-plain', 4),
            ('Asyncio', 'tools', 'fas fa-bolt', 5),
            ('Flowise', 'tools', 'fas fa-robot', 6),
        ]

        for name, category, icon, order in skills_data:
            Skill.objects.update_or_create(
                name=name,
                defaults={'category': category, 'icon': icon, 'order': order}
            )

        self.stdout.write(self.style.SUCCESS(f' OK ({len(skills_data)} навыков)'))

    def load_experiences(self):
        self.stdout.write('  → Опыт работы...')

        experiences_data = [
            {
                'title': 'Тимлид университетского проекта',
                'company': 'МосПолитех',
                'description': 'Руковожу разработкой офисного пакета на основе исходного кода Apache OpenOffice с последующей специализацией под нужды российского бизнеса и государственного сектора России.',
                'responsibilities': '''Сборка из исходного кода на GitHub с последующими правками кода
Разработка backend-части с доработкой сырых функций OpenOffice
Управление и контроль за выполнением командой разработки поставленных задач
Создание и структуризация упрощённого и более специализированного нового интерфейса
Написание более подробной и понятной пользователю документации по работе с офисным пакетом''',
                'technologies': 'C++, Apache OpenOffice, Bash, Git',
                'start_date': date(2024, 1, 1),
                'is_current': True,
                'order': 1
            },
            {
                'title': 'Руководитель команды разработки',
                'company': 'МосПолитех',
                'description': 'Руководил разработкой скриптов и алгоритмов на Python по проекту расширения веб-доступности «EasyAccess».',
                'responsibilities': '''Разработка backend-части с обработкой API запросов на Django
Управление и контроль за выполнением командой разработки крупных задач
Создание структуры API запросов
Реализация запросов к БД на PostgreSQL
Настройка Docker''',
                'technologies': 'Python, Django, Docker, PostgreSQL',
                'start_date': date(2024, 1, 1),
                'end_date': date(2025, 1, 1),
                'is_current': False,
                'order': 2
            }
        ]

        for exp_data in experiences_data:
            Experience.objects.update_or_create(
                title=exp_data['title'],
                company=exp_data['company'],
                defaults=exp_data
            )

        self.stdout.write(self.style.SUCCESS(f' OK ({len(experiences_data)} записей)'))

    def load_educations(self):
        self.stdout.write('  → Образование...')

        educations_data = [
            {
                'institution': 'Московский Политехнический Университет',
                'institution_short': 'МосПолитех',
                'degree': 'Системная и программная инженерия',
                'education_type': 'university',
                'description': 'Высшее образование по направлению системной и программной инженерии.',
                'achievements': '''Изучение алгоритмов и структур данных
Практика с различными базовыми алгоритмами для низкоуровневых языков
Анализ математических алгоритмов
Изучение С++ в контексте системного программирования
Изучение PostgreSQL и структуры базы данных''',
                'start_year': 2024,
                'is_current': True,
                'icon': 'fas fa-university',
                'order': 1
            },
            {
                'institution': 'Рязанский Государственный Радиотехнический Университет',
                'institution_short': 'РГРТУ',
                'degree': 'Фундаментальная информатика и информационные технологии',
                'education_type': 'university',
                'description': 'Высшее образование в области информационных технологий.',
                'achievements': '''Создание, поддержка и администрирование информационно-коммуникационных систем и баз данных
Разработка и тестирование программного обеспечения
Управление информационными ресурсами
Формирование навыков алгоритмического мышления
Разработка оригинальных алгоритмов и интеллектуальные программные системы''',
                'start_year': 2022,
                'end_year': 2024,
                'is_current': False,
                'icon': 'fas fa-university',
                'order': 2
            },
            {
                'institution': 'Яндекс Лицей / Норильск IT-Cube',
                'institution_short': 'Яндекс Лицей',
                'degree': 'Основы промышленного программирования на Python',
                'education_type': 'course',
                'description': 'Продвинутый курс программирования на Python.',
                'achievements': '''Изучение сложных алгоритмов и решение неординарных задач
Работа с фреймворками: Pygame, PyQT, Request, Aiogram и др.
Изучение структуры и создания базы данных SQLite''',
                'start_year': 2021,
                'end_year': 2022,
                'certificate_number': '2202 54726',
                'is_current': False,
                'icon': 'fas fa-graduation-cap',
                'order': 3
            },
            {
                'institution': 'Яндекс Лицей / Норильск IT-Cube',
                'institution_short': 'Яндекс Лицей',
                'degree': 'Основы программирования на языке Python',
                'education_type': 'course',
                'description': 'Базовый курс программирования на Python.',
                'achievements': '''Обучение основам и базовым библиотекам
Изучение PEP8''',
                'start_year': 2020,
                'end_year': 2021,
                'certificate_number': '2101 54726',
                'is_current': False,
                'icon': 'fas fa-graduation-cap',
                'order': 4
            },
            {
                'institution': 'Stepik',
                'institution_short': 'Stepik',
                'degree': 'Введение в программирование (C++)',
                'education_type': 'course',
                'description': 'Онлайн-курс по основам программирования на C++.',
                'achievements': '''Практические основы программирования на С++
Изучение базовых конструкций языка''',
                'start_year': 2022,
                'end_year': 2023,
                'certificate_number': '2759904',
                'is_current': False,
                'icon': 'fas fa-laptop-code',
                'order': 5
            },
            {
                'institution': 'Московский Политех',
                'institution_short': 'МосПолитех',
                'degree': 'Управление инвестиционными проектами',
                'education_type': 'course',
                'description': 'Дополнительное образование по управлению проектами.',
                'achievements': '''Обучение основам и продвинутым методам управления инвестиционными проектами
Разработка финансовых моделей
Управление рисками и анализ внутренней и внешней среды проектов
Расчёт бизнес-плана
Изучение «мсп.рф», «Яндекс.трекер» и других бизнес-инструментов''',
                'start_year': 2024,
                'is_current': True,
                'icon': 'fas fa-chart-line',
                'order': 6
            }
        ]

        for edu_data in educations_data:
            Education.objects.update_or_create(
                institution=edu_data['institution'],
                degree=edu_data['degree'],
                defaults=edu_data
            )

        self.stdout.write(self.style.SUCCESS(f' OK ({len(educations_data)} записей)'))

    def load_projects(self):
        self.stdout.write('  → Проекты...')

        projects_data = [
            {
                'title': 'Abobot',
                'slug': 'abobot',
                'short_description': 'Многофункциональный Telegram-бот для упоминания пользователей внутри чатов.',
                'description': 'Многофункциональный Telegram-бот для упоминания пользователей внутри чатов с продвинутой системой распознавания имён и обработки данных.',
                'features': '''9 команд, 8 текстовых ивентов и 4 нативные функции
Распознавание имён и запись в начальной форме
Запись и обработка данных о группах в обширную БД
Конвертация голосовых сообщений в текст при помощи фреймворка gTTS
Сложный алгоритм оповещения пользователя при упоминании имени в чате''',
                'icon': 'fab fa-telegram',
                'technologies': 'Python, Asyncio, SQLite, Aiogram, gTTS, Request',
                'github_url': 'https://github.com/EDeev/abobot',
                'status': 'beta',
                'card_size': 'featured',
                'users_count': '17.3k+',
                'order': 1
            },
            {
                'title': 'Compile Hub',
                'slug': 'compile-hub',
                'short_description': 'Высокопроизводительный асинхронный сервис для веб-IDE с поддержкой множества языков.',
                'description': 'Высокопроизводительный асинхронный сервис на Python для веб-IDE с поддержкой множества языков программирования.',
                'features': '''Асинхронная queue-based архитектура обработки
Мультиязычная компиляция (C++, Python, JavaScript)
Комплексная система безопасности и rate limiting
Встроенная метрика производительности в реальном времени
Полноценный user management с файловой системой''',
                'icon': 'fas fa-terminal',
                'technologies': 'Python, FastAPI, SQLite, Asyncio',
                'status': 'beta',
                'card_size': 'regular',
                'order': 2
            },
            {
                'title': 'Mobiles Dataset',
                'slug': 'mobiles-dataset',
                'short_description': 'Реляционная система на PostgreSQL для каталогизации смартфонов с интерфейсом на PyQT.',
                'description': 'База данных с приложением на Python. Реляционная система на PostgreSQL для каталогизации технических характеристик и ценовой аналитики смартфонов.',
                'features': '''Функциональный интерфейс на PyQT
Нормализованная структура из 5 взаимосвязанных таблиц
Реализованный полный CRUD функционал
Автоматизированный импорт из CSV с валидацией
Оптимизированные индексы для быстрого поиска''',
                'icon': 'fas fa-mobile-alt',
                'technologies': 'Python, PyQT, PostgreSQL, Psycopg2, Pandas',
                'status': 'completed',
                'card_size': 'regular',
                'order': 3
            },
            {
                'title': 'deev.space',
                'slug': 'deev-space',
                'short_description': 'Личный сайт с информацией обо мне, контактной информацией, достижениями и проектами.',
                'description': 'Личный сайт с информацией обо мне, контактной информацией, достижениями и вкладками с проектами.',
                'features': '''Развёртывание сервера на Nginx
Управление сайтом на Django
Разработка интерфейса с использованием Bootstrap и готовых темплейтов
Шаблонизация HTML кода с использованием Jinja логики
Привязка БД и метрик Яндекса''',
                'icon': 'fas fa-globe',
                'technologies': 'Python, Django, SQLite, Nginx, Bootstrap, Request',
                'demo_url': 'https://deev.space',
                'status': 'beta',
                'card_size': 'small',
                'users_count': '20 посещений/мес.',
                'order': 4
            }
        ]

        for proj_data in projects_data:
            Project.objects.update_or_create(
                slug=proj_data['slug'],
                defaults=proj_data
            )

        self.stdout.write(self.style.SUCCESS(f' OK ({len(projects_data)} проектов)'))

    def load_categories(self):
        self.stdout.write('  → Категории блога...')

        categories = [
            ('Технические гайды', 'tech-guides', 'fas fa-book', 1),
            ('Личные истории', 'personal', 'fas fa-user', 2),
            ('Размышления', 'thoughts', 'fas fa-lightbulb', 3),
            ('Достижения', 'achievements', 'fas fa-trophy', 4),
        ]

        for name, slug, icon, order in categories:
            Category.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'order': order}
            )

        self.stdout.write(self.style.SUCCESS(f' OK ({len(categories)} категорий)'))

    def load_achievements(self):
        self.stdout.write('  → Достижения...')

        achievements_category = Category.objects.filter(slug='achievements').first()

        achievements_data = [
            {
                'title': 'Международный конкурс научно-практических работ',
                'slug': 'naukoemkie-tehnologii-2024',
                'sub_title': '2 место в номинации «Научно-исследовательская работа»',
                'excerpt': 'Международный конкурс научно-практических работ и проектов в рамках Международной конференции «Наукоёмкие технологии — основа современного цифрового промышленного производства»',
                'post': '''Получено 2 место в номинации «Научно-исследовательская работа» на Международном конкурсе научно-практических работ и проектов в рамках Международной конференции «Наукоёмкие технологии — основа современного цифрового промышленного производства».

**Тема работы:** «Разработка веб-интерфейса с адаптивным дизайном для пользователей с особыми возможностями здоровья в системе 1С»

Работа была посвящена созданию доступного веб-интерфейса, учитывающего потребности пользователей с ограниченными возможностями здоровья.''',
                'category': achievements_category,
                'is_achievement': True,
                'achievement_icon': 'fas fa-medal',
                'achievement_date': date(2024, 1, 1),
            }
        ]

        for ach_data in achievements_data:
            Article.objects.update_or_create(
                slug=ach_data['slug'],
                defaults=ach_data
            )

        self.stdout.write(self.style.SUCCESS(f' OK ({len(achievements_data)} достижений)'))
