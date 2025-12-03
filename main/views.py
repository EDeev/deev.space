from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
import json
import logging

from .models import (
    Article, Project, Skill, Comment, ArticleLike, CommentLike,
    ContactMessage, Experience, Education, Category, SiteSettings
)
from .forms import RegisterForm, LoginForm, CommentForm, ContactForm

logger = logging.getLogger(__name__)


def get_site_settings():
    """Получение настроек сайта."""
    return SiteSettings.load()


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
        context['featured_projects'] = Project.objects.filter(
            is_visible=True
        ).order_by('order', '-date')[:6]
        context['experiences'] = Experience.objects.all()[:2]

        context['page_title'] = f'{site_settings.owner_name} — {site_settings.owner_title}'
        context[
            'page_description'] = site_settings.site_description or f'Персональный сайт {site_settings.owner_title.lower()} {site_settings.owner_name}'

        return context

    def _get_skills_by_category(self):
        skills = Skill.objects.all()
        categories = {}
        for skill in skills:
            cat_display = skill.get_category_display()
            if cat_display not in categories:
                categories[cat_display] = []
            categories[cat_display].append(skill)
        return categories


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

        context['page_title'] = f'Обо мне — {site_settings.owner_name}'
        context[
            'page_description'] = f'Профессиональный путь, образование и навыки {site_settings.owner_title.lower()} {site_settings.owner_name}'

        return context

    def _get_skills_by_category(self):
        skills = Skill.objects.all()
        categories = {}
        for skill in skills:
            cat_display = skill.get_category_display()
            if cat_display not in categories:
                categories[cat_display] = []
            categories[cat_display].append(skill)
        return categories


class ProjectsView(ListView):
    """Страница проектов."""
    model = Project
    template_name = 'projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = Project.objects.filter(is_visible=True)
        tech_filter = self.request.GET.get('tech')
        status_filter = self.request.GET.get('status')

        if tech_filter:
            queryset = queryset.filter(technologies__icontains=tech_filter)

        # Исправление фильтрации по статусу
        if status_filter:
            if status_filter == 'in_development':
                # Включаем оба статуса: in_development и beta
                queryset = queryset.filter(status__in=['in_development', 'beta'])
            else:
                queryset = queryset.filter(status=status_filter)

        return queryset.order_by('order', '-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = get_site_settings()

        # Получаем все видимые проекты для правильной фильтрации
        base_queryset = Project.objects.filter(is_visible=True)

        tech_filter = self.request.GET.get('tech')
        status_filter = self.request.GET.get('status')

        if tech_filter:
            base_queryset = base_queryset.filter(technologies__icontains=tech_filter)

        # Разделение по статусам с учетом фильтра
        if status_filter == 'completed':
            context['completed_projects'] = base_queryset.filter(status='completed').order_by('order', '-date')
            context['dev_projects'] = Project.objects.none()
        elif status_filter == 'in_development':
            context['completed_projects'] = Project.objects.none()
            context['dev_projects'] = base_queryset.filter(status__in=['in_development', 'beta']).order_by('order',
                                                                                                           '-date')
        else:
            context['completed_projects'] = base_queryset.filter(status='completed').order_by('order', '-date')
            context['dev_projects'] = base_queryset.filter(status__in=['in_development', 'beta']).order_by('order',
                                                                                                           '-date')

        # Все технологии для фильтра
        all_techs = set()
        for project in Project.objects.filter(is_visible=True):
            all_techs.update(project.get_technologies_list())
        context['all_technologies'] = sorted(all_techs)

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
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object

        context['comments'] = article.comments.filter(
            is_approved=True, parent=None
        ).select_related('user').prefetch_related(
            'replies__user', 'replies__replies__user'
        ).order_by('-created_at')

        context['comment_form'] = CommentForm()

        context['user_like'] = None
        if self.request.user.is_authenticated:
            like = ArticleLike.objects.filter(
                article=article, user=self.request.user
            ).first()
            context['user_like'] = like

        context['related_articles'] = Article.objects.filter(
            is_published=True, is_achievement=False, category=article.category
        ).exclude(pk=article.pk)[:3] if article.category else Article.objects.none()

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
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f'Ошибка отправки email: {e}')

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
        'page_title': 'Регистрация — deev.space'
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


@login_required
@require_POST
def toggle_article_like(request, article_id):
    """Лайк/дизлайк статьи."""
    article = get_object_or_404(Article, id=article_id, is_published=True)

    try:
        data = json.loads(request.body)
        is_like = data.get('is_like', True)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    like, created = ArticleLike.objects.get_or_create(
        article=article, user=request.user,
        defaults={'is_like': is_like}
    )

    user_vote = None
    if not created:
        if like.is_like == is_like:
            like.delete()
        else:
            like.is_like = is_like
            like.save()
            user_vote = is_like
    else:
        user_vote = is_like

    return JsonResponse({
        'success': True,
        'likes': article.likes_count,
        'dislikes': article.dislikes_count,
        'user_vote': user_vote
    })


@login_required
@require_POST
def toggle_comment_like(request, comment_id):
    """Лайк/дизлайк комментария."""
    comment = get_object_or_404(Comment, id=comment_id, is_approved=True)

    try:
        data = json.loads(request.body)
        is_like = data.get('is_like', True)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    like, created = CommentLike.objects.get_or_create(
        comment=comment, user=request.user,
        defaults={'is_like': is_like}
    )

    user_vote = None
    if not created:
        if like.is_like == is_like:
            like.delete()
        else:
            like.is_like = is_like
            like.save()
            user_vote = is_like
    else:
        user_vote = is_like

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