import pytest
from django.urls import reverse

from main.models import ArticleView

UA = 'Mozilla/5.0 (X11; Linux x86_64) Firefox/131.0'


@pytest.mark.django_db
@pytest.mark.parametrize('name', ['index', 'about', 'projects', 'achievements', 'contacts', 'blog'])
def test_page_opens(client, name):
    assert client.get(reverse(name), HTTP_USER_AGENT=UA).status_code == 200


@pytest.mark.django_db
def test_sitemap_and_robots(client, article):
    assert client.get('/sitemap.xml').status_code == 200


@pytest.mark.django_db
def test_article_counts_unique_views(client, article):
    url = article.get_absolute_url()
    client.get(url, HTTP_USER_AGENT=UA)
    client.get(url, HTTP_USER_AGENT=UA)
    article.refresh_from_db()
    assert article.views == 2
    assert ArticleView.objects.filter(article=article).count() == 1


@pytest.mark.django_db
def test_bots_do_not_create_unique_views(client, article):
    client.get(article.get_absolute_url(), HTTP_USER_AGENT='Googlebot/2.1')
    assert not ArticleView.objects.exists()


@pytest.mark.django_db
def test_visitor_cookie_is_signed_and_httponly(client):
    response = client.get(reverse('index'), HTTP_USER_AGENT=UA)
    cookie = response.cookies['dspace_vid']
    assert cookie['httponly']
    assert ':' in cookie.value


@pytest.mark.django_db
def test_unknown_page_returns_404(client):
    assert client.get('/no-such-page/', HTTP_USER_AGENT=UA).status_code == 404
