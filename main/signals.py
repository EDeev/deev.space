from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import requests
import logging

from .models import Article

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def publish_to_social_media(sender, instance, created, **kwargs):
    """Автоматическая публикация новой статьи в социальные сети."""
    if not created:
        return

    if not instance.is_published:
        return

    if instance.is_achievement:
        return

    # Telegram
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHANNEL_ID:
        try:
            publish_to_telegram(instance)
            logger.info(f'Статья "{instance.title}" опубликована в Telegram')
        except Exception as e:
            logger.error(f'Ошибка публикации в Telegram: {e}')

    # VK
    if settings.VK_ACCESS_TOKEN and settings.VK_GROUP_ID:
        try:
            publish_to_vk(instance)
            logger.info(f'Статья "{instance.title}" опубликована в VK')
        except Exception as e:
            logger.error(f'Ошибка публикации в VK: {e}')


def publish_to_telegram(article):
    """Публикация статьи в Telegram-канал."""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    channel_id = settings.TELEGRAM_CHANNEL_ID

    article_url = f"https://deev.space{article.get_absolute_url()}"

    text = f"📝 *{escape_markdown(article.title)}*\n\n"
    if article.excerpt:
        excerpt = article.excerpt[:200] + '...' if len(article.excerpt) > 200 else article.excerpt
        text += f"{escape_markdown(excerpt)}\n\n"
    text += f"[Читать полностью]({article_url})"

    if article.img:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        data = {
            'chat_id': channel_id,
            'photo': f"https://deev.space{article.img.url}",
            'caption': text,
            'parse_mode': 'Markdown'
        }
    else:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': channel_id,
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False
        }

    response = requests.post(url, data=data, timeout=10)
    response.raise_for_status()


def publish_to_vk(article):
    """Публикация статьи в группу VKontakte."""
    access_token = settings.VK_ACCESS_TOKEN
    group_id = settings.VK_GROUP_ID

    article_url = f"https://deev.space{article.get_absolute_url()}"

    message = f"📝 {article.title}\n\n"
    if article.excerpt:
        excerpt = article.excerpt[:300] + '...' if len(article.excerpt) > 300 else article.excerpt
        message += f"{excerpt}\n\n"
    message += f"🔗 Читать: {article_url}"

    url = "https://api.vk.com/method/wall.post"
    params = {
        'owner_id': f'-{group_id}',
        'message': message,
        'from_group': 1,
        'access_token': access_token,
        'v': '5.131'
    }

    if article.img:
        params['attachments'] = f"https://deev.space{article.img.url}"

    response = requests.post(url, params=params, timeout=10)
    response.raise_for_status()


def escape_markdown(text):
    """Экранирование специальных символов Markdown."""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text