from unittest import mock

import pytest

from main.forms import CommentForm, ContactForm
from main.middleware import client_ip_hash, is_bot
from main.models import is_public_http_url
from main.signals import build_telegram_text
from main.templatetags.custom_filters import render_tech_badge


def test_comment_form_strips_scripts_and_keeps_allowed_tags():
    form = CommentForm(data={'content': '<script>alert(1)</script><b>жирный</b> https://example.com'})
    assert form.is_valid()
    content = form.cleaned_data['content']
    assert '<script>' not in content
    assert '<b>жирный</b>' in content
    assert '<a href="https://example.com"' in content


def test_contact_form_removes_all_html():
    data = {'name': 'Иван', 'email': 'ivan@example.com', 'subject': 'Вопрос',
            'message': '<img src=x onerror=alert(1)>Привет', 'captcha': 'token'}
    with mock.patch('main.forms.SmartCaptchaField._verify_captcha', return_value=True):
        form = ContactForm(data=data)
        assert form.is_valid(), form.errors
    assert form.cleaned_data['message'] == 'Привет'


def test_contact_form_rejects_failed_captcha():
    data = {'name': 'Бот', 'email': 'bot@example.com', 'subject': 'Спам', 'message': 'Спам', 'captcha': 'bad'}
    with mock.patch('main.forms.SmartCaptchaField._verify_captcha', return_value=False):
        assert not ContactForm(data=data).is_valid()


def test_tech_badge_escapes_name():
    html = render_tech_badge('<script>x</script>')
    assert '<script>' not in html
    assert '&lt;script&gt;' in html


def test_telegram_text_is_html_escaped(db):
    from main.models import Article

    article = Article(title='C++ & <Rust>', slug='cpp', post='...', excerpt='a < b')
    text = build_telegram_text(article)
    assert '<b>C++ &amp; &lt;Rust&gt;</b>' in text
    assert 'a &lt; b' in text
    assert '\\' not in text


@pytest.mark.parametrize('url', ['file:///etc/passwd', 'ftp://example.com', 'http://localhost/', 'http://10.0.0.1/'])
def test_preview_rejects_non_public_urls(url):
    assert not is_public_http_url(url)


def test_preview_accepts_public_url():
    public = [(2, 1, 6, '', ('93.184.215.14', 443))]
    with mock.patch('main.models.socket.getaddrinfo', return_value=public):
        assert is_public_http_url('https://example.com/page')


def test_ip_hash_is_empty_for_private_addresses(rf):
    assert client_ip_hash(rf.get('/', REMOTE_ADDR='192.168.1.10')) == ''
    assert client_ip_hash(rf.get('/', REMOTE_ADDR='93.184.215.14'))


@pytest.mark.parametrize(('ua', 'expected'), [
    ('', True), ('Googlebot/2.1', True), ('python-requests/2.32', True),
    ('Mozilla/5.0 (Windows NT 10.0) Chrome/129.0', False),
])
def test_bot_detection(rf, ua, expected):
    assert is_bot(rf.get('/', HTTP_USER_AGENT=ua)) is expected
