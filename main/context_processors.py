from .models import SiteSettings


def site_settings(request):
    """Глобальный контекст с настройками сайта."""
    return {
        'global_settings': SiteSettings.load()
    }