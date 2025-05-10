# Личный сайт deev.space

## Технический стек

- **Фреймворк**: Django 4.2+
- **Языки программирования**: Python 3.8+
- **База данных**: SQLite
- **Фронтенд**: HTML, CSS, JavaScript
- **Шаблонизатор**: Django Templates
- **Дополнительные библиотеки**: 
  - Bootstrap для адаптивного дизайна
  - jQuery
  - AOS для анимаций при прокрутке
  - Jarallax для параллакс-эффектов

## Структура проекта

```
deev.space/
├── main_page/               # Основное приложение Django
│   ├── migrations/          # Миграции базы данных
│   ├── models.py            # Определения моделей данных
│   ├── views.py             # Представления/контроллеры
│   ├── urls.py              # URL-маршруты приложения
│   ├── admin.py             # Конфигурация административной панели
│   ├── apps.py              # Конфигурация приложения
│   └── tests.py             # Тесты
├── space/                   # Основной проект Django
│   ├── settings.py          # Настройки проекта
│   ├── urls.py              # Корневые URL-маршруты
│   ├── wsgi.py              # WSGI-конфигурация
│   └── asgi.py              # ASGI-конфигурация
├── templates/               # HTML-шаблоны
│   ├── wrapper.html         # Базовый шаблон сайта
│   ├── metrika.html         # Яндекс.Метрика
│   ├── errors/              # Шаблоны страниц ошибок
│   └── unfold/              # Шаблоны основных страниц
│       ├── index.html       # Главная страница
│       ├── page_article.html # Шаблон статьи
│       └── includes/        # Подключаемые компоненты
├── media/                   # Медиа-файлы, загружаемые пользователями
│   └── sitemap.xml          # Карта сайта
├── static/                  # Статические файлы (CSS, JS, изображения)
│   └── unfold/              # Тема оформления
└── manage.py                # Утилита управления Django
```

## Модели данных

Проект использует три основные модели данных:

1. **Articles** - статьи/публикации
   - `sub_title`: подзаголовок
   - `title`: заголовок
   - `url`: URL-адрес
   - `post_title`: заголовок статьи
   - `post`: содержание статьи
   - `img`: изображение
   - `author`: автор
   - `date`: дата публикации

2. **Projects** - проекты
   - `title`: название проекта
   - `url`: URL-адрес проекта
   - `htegs`: теги для фильтрации (html, cpp, python)
   - `htegs_post`: отображаемые теги
   - `img_main`: главное изображение
   - `img_type`: изображение типа проекта
   - `author`: автор
   - `date`: дата создания

3. **Skills** - навыки
   - `sub_title`: подзаголовок
   - `title`: заголовок
   - `url`: URL-адрес
   - `tegs`: теги
   - `post_title`: заголовок описания
   - `post`: содержание
   - `img`: изображение
   - `author`: автор
   - `date`: дата

## Установка и запуск

### Предварительные требования

- Python 3.8+
- pip (менеджер пакетов Python)
- virtualenv (рекомендуется)

### Шаги по установке

1. Клонирование репозитория:
   ```bash
   git clone https://github.com/IGlek/deev.space.git
   cd deev.space
   ```

2. Создание и активация виртуального окружения:
   ```bash
   python -m venv venv
   # Для Windows
   venv\Scripts\activate
   # Для Linux/Mac
   source venv/bin/activate
   ```

3. Создание структуры базы данных:
   ```bash
   python manage.py migrate
   ```

4. Создание суперпользователя (для администрирования):
   ```bash
   python manage.py createsuperuser
   ```

5. Сбор статических файлов:
   ```bash
   python manage.py collectstatic
   ```
   
   Примечание: В репозитории отсутствуют статические файлы, но они предполагаются в папке `static/`.

6. Запуск сервера для разработки:
   ```bash
   python manage.py runserver
   ```
   
   Сайт будет доступен по адресу: http://127.0.0.1:8000/

## Конфигурация

Основные настройки находятся в файле `space/settings.py`:

- `DEBUG`: для продакшн-среды следует установить `False`
- `ALLOWED_HOSTS`: разрешенные хосты
- `SECRET_KEY`: должен быть изменен в продакшн-среде
- `DATABASES`: конфигурация базы данных

## Структура URL-маршрутов

### Корневые URL-маршруты (space/urls.py)
- `/` - главная страница
- `/admin/` - административная панель Django

## Административная панель

Django-админка доступна по адресу `/admin/` и позволяет управлять:
- Статьями (Articles)
- Проектами (Projects)
- Навыками (Skills)

## Обработка ошибок

Проект включает настраиваемые страницы ошибок:
- 400: Некорректный запрос
- 403: Доступ запрещен
- 404: Страница не найдена
- 500: Внутренняя ошибка сервера

## Развертывание в продакшн

Для развертывания на продакшн-сервере рекомендуется:

1. Настроить веб-сервер (Nginx, Apache) в качестве прокси
2. Использовать WSGI-сервер (Gunicorn, uWSGI) для обработки Django-приложения
3. Включить HTTPS с помощью Let's Encrypt
4. Изменить `DEBUG = False` в settings.py
5. Установить уникальный `SECRET_KEY`
6. Настроить ALLOWED_HOSTS для ваших доменов

Пример конфигурации Nginx:
```nginx
server {
    listen 80;
    server_name deev.space www.deev.space;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/deev.space;
    }
    
    location /media/ {
        root /path/to/deev.space;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/deev.space/deev_space.sock;
    }
}
```

## Интеграция с аналитикой

Проект интегрирован с Яндекс.Метрикой для анализа посещаемости сайта. Код встроен в шаблон `templates/metrika.html`.

## Контактная информация

- Telegram: [@Egor_Deev](https://t.me/Egor_Deev)
- GitHub: [IGlek](https://github.com/IGlek)
- Email: egor@deev.space

## Лицензионная информация

Проект распространяется под лицензией MIT.
