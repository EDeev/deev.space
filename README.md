# deev.space

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Django-4.2+-green.svg" alt="Django Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Beta-orange.svg" alt="Status">
</div>

Личный веб-сайт, разработанный на Django, представляющий портфолио backend-разработчика. Сайт включает информацию о проектах, навыках, статьях и контактах с современным адаптивным дизайном.

## 🌟 Особенности

- **Адаптивный дизайн** с поддержкой всех устройств
- **Система управления контентом** через Django Admin
- **Портфолио проектов** с фильтрацией по технологиям
- **Блог-система** для публикации статей
- **SEO-оптимизация** с sitemap и метатегами
- **Интеграция с аналитикой** (Яндекс.Метрика)
- **Параллакс-эффекты** и плавные анимации

## 🛠 Технологический стек

**Backend:**
- Python 3.8+
- Django 4.2+
- SQLite

**Frontend:**
- HTML5, CSS3, JavaScript
- Bootstrap 5
- jQuery
- AOS (Animate On Scroll)
- Jarallax (параллакс-эффекты)

**Развертывание:**
- Nginx (веб-сервер)
- WSGI/ASGI совместимость

## 📁 Структура проекта

```
deev.space/
├── main_page/              # Django приложение
│   ├── models.py           # Модели данных (Articles, Projects, Skills)
│   ├── views.py            # Представления
│   ├── admin.py            # Административная панель
│   └── urls.py             # URL маршруты
├── space/                  # Настройки Django проекта
│   ├── settings.py         # Конфигурация
│   ├── urls.py             # Корневые URL
│   └── wsgi.py             # WSGI конфигурация
├── templates/              # HTML шаблоны
│   ├── wrapper.html        # Базовый шаблон
│   ├── unfold/             # Шаблоны страниц
│   └── errors/             # Страницы ошибок
├── static/                 # Статические файлы
│   └── unfold/             # CSS, JS, изображения
├── media/                  # Загружаемые файлы
└── requirements.txt        # Зависимости Python
```

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.8+
- pip
- virtualenv (рекомендуется)

### Установка

1. **Клонирование репозитория**
   ```bash
   git clone https://github.com/EDeev/deev.space.git
   cd deev.space
   ```

2. **Создание виртуального окружения**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Установка зависимостей**
   ```bash
   pip install -r requirements.txt
   ```

4. **Применение миграций**
   ```bash
   python manage.py migrate
   ```

5. **Создание суперпользователя**
   ```bash
   python manage.py createsuperuser
   ```

6. **Сбор статических файлов**
   ```bash
   python manage.py collectstatic
   ```

7. **Запуск сервера разработки**
   ```bash
   python manage.py runserver
   ```

Сайт будет доступен по адресу: `http://127.0.0.1:8000`

## 📊 Модели данных

### Articles (Статьи)
- `sub_title` - подзаголовок
- `title` - заголовок
- `url` - URL статьи
- `post_title` - заголовок поста
- `post` - содержание статьи
- `img` - изображение
- `author` - автор
- `date` - дата публикации

### Projects (Проекты)
- `title` - название проекта
- `url` - ссылка на проект
- `htegs` - теги для фильтрации (html, cpp, python)
- `htegs_post` - отображаемые теги
- `img_main` - главное изображение
- `img_type` - иконка типа проекта
- `author` - автор
- `date` - дата создания

### Skills (Навыки)
- `sub_title` - подзаголовок
- `title` - заголовок
- `url` - URL
- `tegs` - теги
- `post_title` - заголовок описания
- `post` - описание навыка
- `img` - изображение
- `author` - автор
- `date` - дата

## ⚙️ Конфигурация

### Основные настройки (`space/settings.py`)

```python
# Для продакшн
DEBUG = False
ALLOWED_HOSTS = ['deev.space', 'www.deev.space']

# Безопасность
SECRET_KEY = 'ваш-уникальный-ключ'

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## 🌐 Развертывание

### Nginx конфигурация

```nginx
server {
    listen 80;
    server_name deev.space www.deev.space;
    
    location /static/ {
        root /path/to/deev.space;
        expires 30d;
    }
    
    location /media/ {
        root /path/to/deev.space;
        expires 30d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Рекомендации для продакшн

- Использовать Gunicorn/uWSGI для WSGI сервера
- Настроить HTTPS с Let's Encrypt
- Установить `DEBUG = False`
- Использовать PostgreSQL вместо SQLite
- Настроить логирование
- Включить Django security middleware

## 📈 Аналитика

Проект интегрирован с Яндекс.Метрикой для отслеживания посещаемости и поведения пользователей.

## 🛡️ Безопасность

- CSRF защита включена
- XSS защита через Django
- Настроенные заголовки безопасности
- Валидация пользовательского ввода

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 👨‍💻 Автор

**Деев Егор Викторович** - Backend Developer  
- GitHub: [@EDeev](https://github.com/EDeev)
- Email: egor@deev.space
- Telegram: [@Egor_Deev](https://t.me/Egor_Deev)

---

<div align="center">
  <p><sub>Создано с ❤️ от вашего дорогого - deev.space ©</sub></p>
</div>
