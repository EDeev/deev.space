import json

import pytest
from django.urls import reverse

from main.models import ArticleLike

PUBLIC_IP = '93.184.215.14'
UA = 'Mozilla/5.0 (X11; Linux x86_64) Firefox/131.0'


def vote(client, article, is_like=True, ip=PUBLIC_IP):
    return client.post(
        reverse('toggle_article_like', args=[article.id]),
        data=json.dumps({'is_like': is_like}),
        content_type='application/json',
        REMOTE_ADDR=ip,
        HTTP_USER_AGENT=UA,
    )


@pytest.mark.django_db
def test_anonymous_like_is_counted(client, article):
    response = vote(client, article)
    assert response.status_code == 200
    assert response.json() == {'success': True, 'likes': 1, 'dislikes': 0, 'user_vote': True}
    assert ArticleLike.objects.get().visitor_id


@pytest.mark.django_db
def test_second_click_removes_vote(client, article):
    vote(client, article)
    response = vote(client, article)
    assert response.json()['user_vote'] is None
    assert ArticleLike.objects.count() == 0


@pytest.mark.django_db
def test_like_switches_to_dislike(client, article):
    vote(client, article, is_like=True)
    response = vote(client, article, is_like=False)
    assert response.json()['likes'] == 0
    assert response.json()['dislikes'] == 1
    assert ArticleLike.objects.count() == 1


@pytest.mark.django_db
def test_votes_per_ip_are_limited(client_factory, article):
    statuses = [vote(client_factory(), article).status_code for _ in range(3)]
    assert statuses == [200, 200, 429]


@pytest.mark.django_db
def test_private_ip_is_not_limited(client_factory, article):
    statuses = [vote(client_factory(), article, ip='10.0.0.5').status_code for _ in range(3)]
    assert statuses == [200, 200, 200]


@pytest.mark.django_db
def test_invalid_json_returns_400(client, article):
    response = client.post(
        reverse('toggle_article_like', args=[article.id]), data='not json', content_type='application/json'
    )
    assert response.status_code == 400


@pytest.fixture
def client_factory():
    from django.test import Client

    return Client
