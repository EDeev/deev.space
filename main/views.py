import json
import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from .forms import CommentForm, ContactForm, LoginForm, RegisterForm
from .middleware import client_ip_hash, is_bot
from .models import (
    Article,
    ArticleLike,
    ArticleView,
    Category,
    Comment,
    CommentLike,
    Education,
    Experience,
    Project,
    SiteSettings,
    Skill,
)

logger = logging.getLogger(__name__)


def get_site_settings():
    """Получение настроек сайта."""
    return SiteSettings.load()


def notify_alertbot_contact_message(message):
    """Уведомление владельца в Telegram (через AlertBot) о новом сообщении с формы обратной связи.

    Не должно ронять отправку формы — все ошибки логируются на уровне вызывающего кода.
    """
    bot_token = settings.ALERTBOT_TOKEN
    chat_id = settings.ALERTBOT_CHAT_ID

    if not bot_token or not chat_id:
        logger.warning('ALERTBOT_TOKEN/ALERTBOT_CHAT_ID не настроены — уведомление о сообщении с формы не отправлено')
        return

    text = (
        f'<b>Новое сообщение с сайта deev.space</b>\n\n'
        f'<b>Имя:</b> {escape(message.name)}\n'
        f'<b>Email:</b> {escape(message.email)}\n'
        f'<b>Тема:</b> {escape(message.subject)}\n\n'
        f'{escape(message.message)}'
    )

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    response = requests.post(url, data={
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
    }, timeout=10)
    response.raise_for_status()



def get_skills_by_category():
    """Навыки по категориям в порядке Skill.CATEGORY_CHOICES."""
    rank = {key: i for i, (key, _) in enumerate(Skill.CATEGORY_CHOICES)}
    skills = sorted(Skill.objects.all(), key=lambda s: (rank.get(s.category, len(rank)), s.order, s.name))
    categories = {}
    for skill in skills:
        categories.setdefault(skill.get_category_display(), []).append(skill)
    return categories


class IndexView(TemplateView):
    """Главная страница."""
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = get_site_settings()

        context['site_settings'] = site_settings
        context['skills'] = Skill.objects.all()
        context['skills_by_category'] = self._get_skills_by_category()
        context['recent_articles'] = Article.objects.filter(
            is_published=True, is_achievement=False
        ).select_related('category')[:3]

        # Только проекты с галочкой "Показывать на главной", сортировка по homepage_order
        context['featured_projects'] = Project.objects.filter(
            is_visible=True,
            show_on_homepage=True
        ).order_by('homepage_order', 'order', '-date')[:6]
        context['more_projects_count'] = max(
            Project.objects.filter(is_visible=True).count() - len(context['featured_projects']), 0
        )

        context['experiences'] = Experience.objects.all()[:2]

        context['page_title'] = f'{site_settings.owner_name} — {site_settings.owner_title}'
        context[
            'page_description'] = site_settings.site_description or f'Персональный сайт {site_settings.owner_title} {site_settings.owner_name}'

        return context

    def _get_skills_by_category(self):
        return get_skills_by_category()


class AboutView(TemplateView):
    """Страница 'Обо мне'."""
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = get_site_settings()

        context['site_settings'] = site_settings
        context['experiences'] = Experience.objects.all()
        context['educations'] = Education.objects.all()
        context['skills'] = Skill.objects.all()
        context['skills_by_category'] = self._get_skills_by_category()
        context['projects_count'] = Project.objects.filter(is_visible=True).count()
        context['skills_count_rounded'] = Skill.objects.count() // 10 * 10
        blog_views = Article.objects.filter(
            is_published=True, is_achievement=False
        ).aggregate(total=Sum('views'))['total'] or 0
        context['blog_views_display'] = (
            f'{blog_views // 100 / 10:g}k+' if blog_views >= 1000 else str(blog_views)
        )

        context['page_title'] = f'Обо мне — {site_settings.owner_name}'
        context[
            'page_description'] = f'Профессиональный путь, образование и навыки {site_settings.owner_title} {site_settings.owner_name}'

        return context

    def _get_skills_by_category(self):
        return get_skills_by_category()


class ProjectsView(ListView):
    """Страница проектов."""
    model = Project
    template_name = 'projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = Project.objects.filter(is_visible=True).select_related('status')

        lang_filter = self.request.GET.get('lang')
        tech_filter = self.request.GET.get('tech')
        status_filter = self.request.GET.get('status')

        if lang_filter:
            queryset = queryset.filter(programming_languages__icontains=lang_filter)

        if tech_filter:
            queryset = queryset.filter(technologies__icontains=tech_filter)

        if status_filter:
            if status_filter == 'completed':
                # Только проекты со статусом, помеченным как is_release
                queryset = queryset.filter(status__is_release=True)
            elif status_filter == 'in_development':
                # Все остальные (не релиз)
                queryset = queryset.filter(
                    Q(status__is_release=False) | Q(status__isnull=True)
                )

        return queryset.order_by('order', '-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = get_site_settings()

        base_queryset = Project.objects.filter(is_visible=True).select_related('status')

        lang_filter = self.request.GET.get('lang')
        tech_filter = self.request.GET.get('tech')
        status_filter = self.request.GET.get('status')

        if lang_filter:
            base_queryset = base_queryset.filter(programming_languages__icontains=lang_filter)
        if tech_filter:
            base_queryset = base_queryset.filter(technologies__icontains=tech_filter)

        # Разделение по статусам
        if status_filter == 'completed':
            context['completed_projects'] = base_queryset.filter(status__is_release=True).order_by('order', '-date')
            context['dev_projects'] = Project.objects.none()
        elif status_filter == 'in_development':
            context['completed_projects'] = Project.objects.none()
            context['dev_projects'] = base_queryset.filter(
                Q(status__is_release=False) | Q(status__isnull=True)
            ).order_by('order', '-date')
        else:
            context['completed_projects'] = base_queryset.filter(status__is_release=True).order_by('order', '-date')
            context['dev_projects'] = base_queryset.filter(
                Q(status__is_release=False) | Q(status__isnull=True)
            ).order_by('order', '-date')

        # Собираем все языки программирования для фильтра
        all_languages = set()
        all_techs = set()
        for project in Project.objects.filter(is_visible=True):
            all_languages.update(project.get_languages_list())
            all_techs.update(project.get_technologies_list())

        context['all_languages'] = sorted(all_languages)
        context['all_technologies'] = sorted(all_techs)

        context['current_lang'] = self.request.GET.get('lang', '')
        context['current_tech'] = self.request.GET.get('tech', '')
        context['current_status'] = self.request.GET.get('status', '')

        context['page_title'] = f'Проекты — {site_settings.owner_name}'
        context[
            'page_description'] = 'Портфолио проектов: Telegram-боты, веб-приложения, базы данных и инструменты разработки'

        return context


class BlogView(ListView):
    """Страница блога."""
    model = Article
    template_name = 'blog/blog.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        queryset = Article.objects.filter(
            is_published=True, is_achievement=False
        ).select_related('category')

        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(post__icontains=search_query)
            )

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = get_site_settings()

        context['categories'] = Category.objects.annotate(
            count=Count('articles', filter=Q(articles__is_published=True, articles__is_achievement=False))
        ).filter(count__gt=0)

        category_slug = self.kwargs.get('category_slug')
        context['current_category'] = None
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)

        context['search_query'] = self.request.GET.get('q', '')
        context['total_articles'] = Article.objects.filter(is_published=True, is_achievement=False).count()

        context['page_title'] = f'Блог — {site_settings.owner_name}'
        context['page_description'] = 'Технические статьи, гайды и размышления о разработке'

        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ArticleDetailView(DetailView):
    """Страница отдельной статьи."""
    model = Article
    template_name = 'blog/article.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related('category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save(update_fields=['views'])
        visitor_id = getattr(self.request, 'visitor_id', '')
        if visitor_id and not is_bot(self.request):
            ArticleView.objects.get_or_create(article=obj, visitor_id=visitor_id)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object

        # Комментарии только если включены
        if article.comments_enabled:
            context['comments'] = article.comments.filter(
                is_approved=True, parent=None
            ).select_related('user').prefetch_related(
                'replies__user', 'replies__replies__user'
            ).order_by('-created_at')
        else:
            context['comments'] = []

        context['comment_form'] = CommentForm()

        context['user_like'] = None
        if self.request.user.is_authenticated:
            like = ArticleLike.objects.filter(
                article=article, user=self.request.user
            ).first()
            context['user_like'] = like
        elif getattr(self.request, 'visitor_id', ''):
            context['user_like'] = ArticleLike.objects.filter(
                article=article, user__isnull=True, visitor_id=self.request.visitor_id
            ).first()

        context['related_articles'] = Article.objects.filter(
            is_published=True, is_achievement=False, category=article.category
        ).exclude(pk=article.pk)[:3] if article.category else Article.objects.none()

        # Галерея изображений
        gallery_images = article.gallery_images.all()
        if article.exclude_inline_from_blocks:
            gallery_images = gallery_images.filter(is_inline=False)
        context['gallery_images'] = gallery_images

        # Прикреплённые файлы
        attached_files = article.attached_files.all()
        if article.exclude_inline_from_blocks:
            attached_files = attached_files.filter(is_inline=False)
        context['attached_files'] = attached_files

        # Прикреплённые ссылки
        attached_links = article.attached_links.all()
        if article.exclude_inline_from_blocks:
            attached_links = attached_links.filter(is_inline=False)
        context['attached_links'] = attached_links

        context['page_title'] = f'{article.title} — Блог'
        context['page_description'] = article.excerpt or article.post[:160]
        context['og_image'] = article.img.url if article.img else None

        return context


class AchievementsView(ListView):
    """Страница достижений."""
    model = Article
    template_name = 'achievements.html'
    context_object_name = 'achievements'

    def get_queryset(self):
        return Article.objects.filter(
            is_published=True, is_achievement=True
        ).order_by('-achievement_date', '-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = get_site_settings()

        context['page_title'] = f'Достижения — {site_settings.owner_name}'
        context['page_description'] = 'Награды, сертификаты и профессиональные достижения'

        return context


class ContactsView(TemplateView):
    """Страница контактов."""
    template_name = 'contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = get_site_settings()

        context['site_settings'] = site_settings
        context['contact_form'] = ContactForm()

        context['smartcaptcha_client_key'] = settings.SMARTCAPTCHA_CLIENT_KEY

        context['page_title'] = f'Контакты — {site_settings.owner_name}'
        context['page_description'] = 'Свяжитесь со мной: Telegram, email, социальные сети и форма обратной связи'

        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save()

            try:
                send_mail(
                    subject=f'[deev.space] Новое сообщение: {message.subject}',
                    message=f'От: {message.name} ({message.email})\n\nТема: {message.subject}\n\n{message.message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                )
            except Exception:
                logger.exception('Ошибка отправки email')

            try:
                notify_alertbot_contact_message(message)
            except Exception as e:
                logger.error(f'Ошибка отправки уведомления в AlertBot: {e}')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Сообщение успешно отправлено!'})

            messages.success(request, 'Сообщение успешно отправлено!')
            return redirect('contacts')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        context = self.get_context_data()
        context['contact_form'] = form
        return render(request, self.template_name, context)


def register_view(request):
    """Регистрация пользователя."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')

            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {
        'form': form,
        'page_title': 'Регистрация — deev.space',
        'smartcaptcha_client_key': settings.SMARTCAPTCHA_CLIENT_KEY
    })


def login_view(request):
    """Авторизация пользователя."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'С возвращением, {user.username}!')

            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {
        'form': form,
        'page_title': 'Вход — deev.space'
    })


def logout_view(request):
    """Выход из системы."""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')


@login_required
@require_POST
def add_comment(request, article_id):
    """Добавление комментария к статье."""
    article = get_object_or_404(Article, id=article_id, is_published=True)

    # Проверяем, включены ли комментарии
    if not article.comments_enabled:
        return JsonResponse({'success': False, 'error': 'Комментарии отключены для этой статьи'}, status=403)

    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.user = request.user

        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id, article=article)
            if parent.nesting_level < 3:
                comment.parent = parent

        comment.save()

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'user': comment.user.username,
                'avatar_letter': comment.user.get_avatar_letter(),
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                'likes': 0,
                'dislikes': 0,
            }
        })

    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


VOTES_PER_IP_PER_DAY = 2


def _toggle_vote(request, model, field, obj):
    """Общая логика лайка/дизлайка: по аккаунту для вошедших, по ID посетителя для остальных."""
    try:
        is_like = bool(json.loads(request.body).get('is_like', True))
    except (json.JSONDecodeError, AttributeError):
        return None, JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    qs = model.objects.filter(**{field: obj})
    if request.user.is_authenticated:
        mine = qs.filter(user=request.user)
    else:
        mine = qs.filter(user__isnull=True, visitor_id=request.visitor_id)
    vote = mine.first()

    if vote:
        if vote.is_like == is_like:
            vote.delete()
            return None, None
        vote.is_like = is_like
        vote.save(update_fields=['is_like'])
        return is_like, None

    ip_hash = client_ip_hash(request)
    if not request.user.is_authenticated and ip_hash:
        recent = qs.filter(user__isnull=True, ip_hash=ip_hash,
                           created_at__gte=timezone.now() - timedelta(days=1)).count()
        if recent >= VOTES_PER_IP_PER_DAY:
            return None, JsonResponse(
                {'success': False, 'error': 'Слишком много оценок с этого устройства, попробуйте позже'}, status=429
            )
    model.objects.create(
        **{field: obj}, is_like=is_like, ip_hash=ip_hash,
        user=request.user if request.user.is_authenticated else None,
        visitor_id='' if request.user.is_authenticated else request.visitor_id,
    )
    return is_like, None


@require_POST
def toggle_article_like(request, article_id):
    """Лайк/дизлайк статьи (в том числе достижения), без регистрации."""
    article = get_object_or_404(Article, id=article_id, is_published=True)
    user_vote, error = _toggle_vote(request, ArticleLike, 'article', article)
    if error:
        return error
    return JsonResponse({
        'success': True,
        'likes': article.likes_count,
        'dislikes': article.dislikes_count,
        'user_vote': user_vote
    })


@require_POST
def toggle_comment_like(request, comment_id):
    """Лайк/дизлайк комментария, без регистрации."""
    comment = get_object_or_404(Comment, id=comment_id, is_approved=True)
    user_vote, error = _toggle_vote(request, CommentLike, 'comment', comment)
    if error:
        return error
    return JsonResponse({
        'success': True,
        'likes': comment.likes_count,
        'dislikes': comment.dislikes_count,
        'user_vote': user_vote
    })


def handler404(request, exception):
    """Обработчик ошибки 404."""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """Обработчик ошибки 500."""
    return render(request, 'errors/500.html', status=500)
