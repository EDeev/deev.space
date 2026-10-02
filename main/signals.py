import html
import logging

import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Article

logger = logging.getLogger(__name__)

SITE_URL = 'https://deev.space'


@receiver(post_save, sender=Article)
def publish_to_social_media(sender, instance, created, **kwargs):
    """Автоматическая публикация новой статьи в социальные сети."""
    if not created or not instance.is_published or instance.is_achievement:
        return

    if settings.SOCIAL_AUTOPOST:
        if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHANNEL_ID:
            try:
                publish_to_telegram(instance)
                logger.info('Статья "%s" опубликована в Telegram', instance.title)
            except requests.RequestException:
                logger.exception('Ошибка публикации в Telegram')

        if settings.VK_ACCESS_TOKEN and settings.VK_GROUP_ID:
            try:
                publish_to_vk(instance)
                logger.info('Статья "%s" опубликована в VK', instance.title)
            except requests.RequestException:
                logger.exception('Ошибка публикации в VK')

    ping_search_engines()


def build_telegram_text(article):
    """Текст поста для Telegram в режиме parse_mode=HTML."""
    article_url = f'{SITE_URL}{article.get_absolute_url()}'
    text = f'📝 <b>{html.escape(article.title)}</b>\n\n'
    if article.excerpt:
        excerpt = article.excerpt[:200] + '...' if len(article.excerpt) > 200 else article.excerpt
        text += f'{html.escape(excerpt)}\n\n'
    text += f'<a href="{html.escape(article_url, quote=True)}">Читать полностью</a>'
    return text


def publish_to_telegram(article):
    """Публикация статьи в Telegram-канал."""
    api = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}'
    text = build_telegram_text(article)

    if article.img:
        url = f'{api}/sendPhoto'
        data = {
            'chat_id': settings.TELEGRAM_CHANNEL_ID,
            'photo': f'{SITE_URL}{article.img.url}',
            'caption': text,
            'parse_mode': 'HTML',
        }
    else:
        url = f'{api}/sendMessage'
        data = {
            'chat_id': settings.TELEGRAM_CHANNEL_ID,
            'text': text,
            'parse_mode': 'HTML',
        }

    response = requests.post(url, data=data, timeout=10)
    response.raise_for_status()


def publish_to_vk(article):
    """Публикация статьи в группу VKontakte."""
    article_url = f'{SITE_URL}{article.get_absolute_url()}'

    message = f'📝 {article.title}\n\n'
    if article.excerpt:
        excerpt = article.excerpt[:300] + '...' if len(article.excerpt) > 300 else article.excerpt
        message += f'{excerpt}\n\n'
    message += f'🔗 Читать: {article_url}'

    params = {
        'owner_id': f'-{settings.VK_GROUP_ID}',
        'message': message,
        'from_group': 1,
        'access_token': settings.VK_ACCESS_TOKEN,
        'v': '5.131',
    }
    if article.img:
        params['attachments'] = f'{SITE_URL}{article.img.url}'

    response = requests.post('https://api.vk.com/method/wall.post', params=params, timeout=10)
    response.raise_for_status()


def ping_search_engines():
    """Уведомление Яндекса об обновлении sitemap (Google ping-эндпоинт отключил в 2023 году)."""
    try:
        requests.get(f'https://webmaster.yandex.ru/ping?sitemap={SITE_URL}/sitemap.xml', timeout=5)
    except requests.RequestException as e:
        logger.warning('Ошибка ping Яндекса: %s', e)
