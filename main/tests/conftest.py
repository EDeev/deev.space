import pytest

from main.models import Article, SiteSettings


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Никаких реальных запросов наружу: ping поисковиков и т. п."""
    calls = []
    monkeypatch.setattr('main.signals.requests.get', lambda *a, **kw: calls.append((a, kw)))
    monkeypatch.setattr('main.signals.requests.post', lambda *a, **kw: calls.append((a, kw)))
    return calls


@pytest.fixture
def article(db):
    return Article.objects.create(title='Первая статья', post='Текст статьи', excerpt='Кратко')


@pytest.fixture
def site_settings(db):
    return SiteSettings.load()
