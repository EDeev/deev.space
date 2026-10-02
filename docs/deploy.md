# Развёртывание

## Docker

```bash
cp .env.example .env    # задайте DJANGO_SECRET_KEY и при необходимости ключи капчи и почты
docker compose up -d
docker compose exec web python manage.py createsuperuser
```

База и загруженные файлы хранятся в томе `data` (`/data/db.sqlite3`, `/data/media`). Готовый образ
собирается GitHub Actions на каждый тег `v*`:

```bash
docker pull ghcr.io/edeev/deev.space:latest
docker pull dcr.deev.su/edeev/deev.space:latest
```

За обратным прокси укажите домены в `DJANGO_ALLOWED_HOSTS` и `DJANGO_CSRF_TRUSTED_ORIGINS`, а
`DJANGO_SERVE_MEDIA` выключите и отдавайте `/media/` прокси-сервером.

## Как работает deev.space

Боевой сайт крутится на VPS без Docker:

- gunicorn под отдельным пользователем `dspace`, systemd-юнит, unix-сокет;
- nginx отдаёт `/static/` и `/media/` с диска и проксирует остальное в сокет, TLS — Let's Encrypt;
- переменные окружения — в `.env` рядом с проектом;
- обновление: выложить код, `pip install -r requirements.txt`, `python manage.py migrate`,
  `python manage.py collectstatic --noinput`, перезапуск юнита;
- доступность сайта и срок сертификата проверяет Prometheus (blackbox exporter), уведомления
  о новых сообщениях с формы приходят в Telegram через AlertBot.
