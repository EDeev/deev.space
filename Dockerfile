FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DB_PATH=/data/db.sqlite3 \
    DJANGO_MEDIA_ROOT=/data/media

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput \
    && useradd --create-home --uid 1000 app \
    && mkdir -p /data/media logs \
    && chown -R app:app /data logs

USER app
VOLUME ["/data"]
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn dspace.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -"]
