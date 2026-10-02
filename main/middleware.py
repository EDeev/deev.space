"""Анонимный идентификатор посетителя (для оценок и уникальных просмотров без регистрации)."""
import hashlib
import ipaddress
import uuid

from django.conf import settings

COOKIE = 'dspace_vid'
SALT = 'dspace-visitor'
MAX_AGE = 365 * 24 * 3600


class VisitorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        vid = request.get_signed_cookie(COOKIE, default=None, salt=SALT)
        fresh = not vid
        if fresh:
            vid = uuid.uuid4().hex
        request.visitor_id = vid
        response = self.get_response(request)
        if fresh:
            response.set_signed_cookie(
                COOKIE, vid, salt=SALT, max_age=MAX_AGE, httponly=True,
                secure=not settings.DEBUG, samesite='Lax'
            )
        return response


def client_ip_hash(request):
    """Хэш IP + User-Agent с солью; пустая строка, если реальный IP не виден (loopback/частная сеть)."""
    ip = (request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR') or '').strip()
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ''
    if addr.is_loopback or addr.is_private:
        return ''
    ua = request.META.get('HTTP_USER_AGENT', '')
    return hashlib.sha256(f'{settings.SECRET_KEY}|{ip}|{ua}'.encode()).hexdigest()


BOT_MARKERS = ('bot', 'spider', 'crawl', 'slurp', 'preview', 'curl', 'wget', 'python-requests', 'headless')


def is_bot(request):
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    return not ua or any(m in ua for m in BOT_MARKERS)
