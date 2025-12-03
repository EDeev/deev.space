from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class CustomUser(AbstractUser):
    """Расширенная модель пользователя с упрощённой регистрацией."""
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    is_verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def get_avatar_letter(self):
        return self.username[0].upper() if self.username else 'U'


class Category(models.Model):
    """Категории для статей блога."""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=50, blank=True, default='fas fa-folder', verbose_name='Иконка')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_category', kwargs={'category_slug': self.slug})

    @property
    def articles_count(self):
        return self.articles.filter(is_published=True).count()


class Article(models.Model):
    """Модель статей блога и достижений."""

    GALLERY_DISPLAY_CHOICES = [
        ('carousel', 'Карусель'),
        ('collage', 'Коллаж'),
    ]

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    sub_title = models.CharField(max_length=300, blank=True, verbose_name='Подзаголовок')
    excerpt = models.TextField(max_length=500, blank=True, verbose_name='Краткое описание')
    post = models.TextField(verbose_name='Содержание')
    img = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Превью (обложка)')
    show_cover_in_article = models.BooleanField(default=True, verbose_name='Показывать обложку в начале статьи')
    gallery_display_mode = models.CharField(
        max_length=20,
        choices=GALLERY_DISPLAY_CHOICES,
        default='carousel',
        verbose_name='Режим отображения галереи'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='articles', verbose_name='Категория'
    )
    author = models.CharField(max_length=100, default='Егор Деев', verbose_name='Автор')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    comments_enabled = models.BooleanField(default=True, verbose_name='Включить комментарии')
    exclude_inline_from_blocks = models.BooleanField(
        default=False,
        verbose_name='Не дублировать медиа из редактора в блоках',
        help_text='Если включено, изображения/файлы/ссылки, добавленные через редактор в текст, не будут отображаться в общих блоках'
    )
    is_achievement = models.BooleanField(default=False, verbose_name='Это достижение')
    achievement_icon = models.CharField(
        max_length=50, blank=True, default='fas fa-trophy',
        verbose_name='Иконка достижения'
    )
    achievement_date = models.DateField(blank=True, null=True, verbose_name='Дата достижения')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.title))
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.excerpt and self.post:
            self.excerpt = self.post[:300] + '...' if len(self.post) > 300 else self.post
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    @property
    def likes_count(self):
        return self.likes.filter(is_like=True).count()

    @property
    def dislikes_count(self):
        return self.likes.filter(is_like=False).count()

    @property
    def comments_count(self):
        return self.comments.filter(is_approved=True).count()


class ArticleImage(models.Model):
    """Изображения для статьи (галерея)."""
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name='Статья'
    )
    image = models.ImageField(upload_to='articles/gallery/', verbose_name='Изображение')
    caption = models.CharField(max_length=255, blank=True, verbose_name='Подпись')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_inline = models.BooleanField(
        default=False,
        verbose_name='Добавлено через редактор',
        help_text='Отметьте, если это изображение вставлено в текст статьи'
    )

    class Meta:
        verbose_name = 'Изображение статьи'
        verbose_name_plural = 'Изображения статьи'
        ordering = ['order']

    def __str__(self):
        return f"Изображение для {self.article.title}"


class ArticleFile(models.Model):
    """Прикреплённые файлы к статье."""
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        related_name='attached_files',
        verbose_name='Статья'
    )
    file = models.FileField(upload_to='articles/files/', verbose_name='Файл')
    title = models.CharField(max_length=255, verbose_name='Название файла')
    description = models.TextField(blank=True, verbose_name='Описание')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_inline = models.BooleanField(
        default=False,
        verbose_name='Добавлено через редактор',
        help_text='Отметьте, если ссылка на этот файл вставлена в текст статьи'
    )

    class Meta:
        verbose_name = 'Файл статьи'
        verbose_name_plural = 'Файлы статьи'
        ordering = ['order']

    def __str__(self):
        return self.title

    @property
    def file_extension(self):
        return self.file.name.split('.')[-1].upper() if self.file else ''

    @property
    def file_size(self):
        if self.file:
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return ''


class ArticleLink(models.Model):
    """Ссылки, прикреплённые к статье."""
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        related_name='attached_links',
        verbose_name='Статья'
    )
    url = models.URLField(verbose_name='URL')
    title = models.CharField(max_length=255, blank=True, verbose_name='Заголовок')
    description = models.TextField(blank=True, verbose_name='Описание')
    preview_image = models.URLField(blank=True, verbose_name='URL изображения превью')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_inline = models.BooleanField(
        default=False,
        verbose_name='Добавлено через редактор',
        help_text='Отметьте, если эта ссылка вставлена в текст статьи'
    )

    class Meta:
        verbose_name = 'Ссылка статьи'
        verbose_name_plural = 'Ссылки статьи'
        ordering = ['order']

    def __str__(self):
        return self.title or self.url

    @property
    def domain(self):
        parsed = urlparse(self.url)
        return parsed.netloc

    def fetch_preview(self):
        """Автоматическое получение метаданных ссылки."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; ArticleBot/1.0)'}
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Получаем заголовок
            og_title = soup.find('meta', property='og:title')
            if og_title:
                self.title = og_title.get('content', '')[:255]
            elif soup.title:
                self.title = soup.title.string[:255] if soup.title.string else ''

            # Получаем описание
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                self.description = og_desc.get('content', '')
            else:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    self.description = meta_desc.get('content', '')

            # Получаем изображение
            og_image = soup.find('meta', property='og:image')
            if og_image:
                self.preview_image = og_image.get('content', '')

        except Exception:
            pass

    def save(self, *args, **kwargs):
        if not self.title:
            self.fetch_preview()
        super().save(*args, **kwargs)


class ProjectStatus(models.Model):
    """Гибкие статусы проектов."""
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Код')
    color = models.CharField(max_length=20, default='primary', verbose_name='Цвет (CSS класс)')
    is_release = models.BooleanField(
        default=False,
        verbose_name='Это релиз',
        help_text='Проекты с этим статусом попадают в "Завершённые"'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Статус проекта'
        verbose_name_plural = 'Статусы проектов'
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


class Project(models.Model):
    """Модель проектов портфолио."""
    SIZE_CHOICES = [
        ('featured', 'Главный (большой)'),
        ('regular', 'Обычный'),
        ('small', 'Компактный'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    short_description = models.CharField(max_length=300, verbose_name='Краткое описание')
    description = models.TextField(verbose_name='Полное описание')
    features = models.TextField(blank=True, verbose_name='Особенности (каждая с новой строки)')
    img_main = models.ImageField(upload_to='projects/', blank=True, null=True, verbose_name='Главное изображение')
    icon = models.CharField(max_length=50, default='fas fa-code', verbose_name='Иконка проекта')

    # Разделение на языки и технологии
    programming_languages = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Языки программирования (через запятую)',
        help_text='Например: Python, JavaScript'
    )
    technologies = models.CharField(
        max_length=500,
        verbose_name='Технологии (через запятую)',
        help_text='Например: Django, React, PostgreSQL'
    )

    github_url = models.URLField(blank=True, verbose_name='GitHub')
    demo_url = models.URLField(blank=True, verbose_name='Демо/Ссылка')

    status = models.ForeignKey(
        ProjectStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Статус'
    )
    card_size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='regular', verbose_name='Размер карточки')
    users_count = models.CharField(max_length=50, blank=True, verbose_name='Количество пользователей')
    author = models.CharField(max_length=100, default='Егор Деев', verbose_name='Автор')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')
    is_visible = models.BooleanField(default=True, verbose_name='Отображать')

    # Поля для главной страницы
    show_on_homepage = models.BooleanField(default=False, verbose_name='Показывать на главной')
    homepage_order = models.PositiveIntegerField(default=0, verbose_name='Порядок на главной')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['order', '-date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    def get_technologies_list(self):
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]

    def get_languages_list(self):
        if not self.programming_languages:
            return []
        return [lang.strip() for lang in self.programming_languages.split(',') if lang.strip()]

    def get_features_list(self):
        if not self.features:
            return []
        return [f.strip() for f in self.features.split('\n') if f.strip()]

    @property
    def is_completed(self):
        """Проект считается завершённым, если его статус помечен как релиз."""
        return self.status and self.status.is_release


class Skill(models.Model):
    """Модель навыков и технологий."""
    CATEGORY_CHOICES = [
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('devops', 'DevOps'),
        ('database', 'Database'),
        ('tools', 'Tools'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    icon = models.CharField(max_length=100, blank=True, verbose_name='CSS класс иконки')
    icon_svg = models.TextField(blank=True, verbose_name='SVG иконка')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Experience(models.Model):
    """Модель опыта работы."""
    title = models.CharField(max_length=200, verbose_name='Должность')
    company = models.CharField(max_length=200, verbose_name='Компания')
    company_url = models.URLField(blank=True, verbose_name='Сайт компании')
    description = models.TextField(verbose_name='Описание')
    responsibilities = models.TextField(blank=True, verbose_name='Обязанности (каждая с новой строки)')
    technologies = models.CharField(max_length=500, blank=True, verbose_name='Технологии')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    is_current = models.BooleanField(default=False, verbose_name='Текущее место работы')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Опыт работы'
        verbose_name_plural = 'Опыт работы'
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.title} — {self.company}"

    def get_responsibilities_list(self):
        if not self.responsibilities:
            return []
        return [r.strip() for r in self.responsibilities.split('\n') if r.strip()]

    def get_technologies_list(self):
        if not self.technologies:
            return []
        return [t.strip() for t in self.technologies.split(',') if t.strip()]

    @property
    def duration(self):
        end = self.end_date or __import__('datetime').date.today()
        months = (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)
        years = months // 12
        remaining_months = months % 12

        parts = []
        if years:
            parts.append(f"{years} {'год' if years == 1 else 'года' if 2 <= years <= 4 else 'лет'}")
        if remaining_months:
            parts.append(
                f"{remaining_months} {'месяц' if remaining_months == 1 else 'месяца' if 2 <= remaining_months <= 4 else 'месяцев'}")
        return ' '.join(parts) if parts else 'Менее месяца'


class Education(models.Model):
    """Модель образования."""
    TYPE_CHOICES = [
        ('university', 'Высшее образование'),
        ('course', 'Курс/Сертификат'),
        ('school', 'Школа/Лицей'),
    ]

    institution = models.CharField(max_length=300, verbose_name='Учебное заведение')
    institution_short = models.CharField(max_length=100, blank=True, verbose_name='Сокращённое название')
    degree = models.CharField(max_length=200, verbose_name='Специальность/Программа')
    education_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='university', verbose_name='Тип')
    description = models.TextField(blank=True, verbose_name='Описание')
    achievements = models.TextField(blank=True, verbose_name='Достижения (каждое с новой строки)')
    start_year = models.PositiveIntegerField(verbose_name='Год начала')
    end_year = models.PositiveIntegerField(null=True, blank=True, verbose_name='Год окончания')
    is_current = models.BooleanField(default=False, verbose_name='В процессе обучения')
    certificate_number = models.CharField(max_length=100, blank=True, verbose_name='Номер сертификата')
    certificate_url = models.URLField(blank=True, verbose_name='Ссылка на сертификат')
    icon = models.CharField(max_length=50, default='fas fa-graduation-cap', verbose_name='Иконка')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образование'
        ordering = ['order', '-start_year']

    def __str__(self):
        return f"{self.degree} — {self.institution_short or self.institution}"

    def get_achievements_list(self):
        if not self.achievements:
            return []
        return [a.strip() for a in self.achievements.split('\n') if a.strip()]


class Comment(models.Model):
    """Модель комментариев к статьям."""
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments', verbose_name='Статья'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments', verbose_name='Пользователь'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='replies', verbose_name='Родительский комментарий'
    )
    content = models.TextField(max_length=2000, verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_approved = models.BooleanField(default=True, verbose_name='Одобрен')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}...'

    @property
    def likes_count(self):
        return self.comment_likes.filter(is_like=True).count()

    @property
    def dislikes_count(self):
        return self.comment_likes.filter(is_like=False).count()

    @property
    def nesting_level(self):
        level = 0
        parent = self.parent
        while parent and level < 3:
            level += 1
            parent = parent.parent
        return level


class ArticleLike(models.Model):
    """Модель лайков/дизлайков статей."""
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='likes', verbose_name='Статья'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='article_likes', verbose_name='Пользователь'
    )
    is_like = models.BooleanField(verbose_name='Лайк')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Оценка статьи'
        verbose_name_plural = 'Оценки статей'
        unique_together = ['article', 'user']


class CommentLike(models.Model):
    """Модель лайков/дизлайков комментариев."""
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name='comment_likes', verbose_name='Комментарий'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comment_likes', verbose_name='Пользователь'
    )
    is_like = models.BooleanField(verbose_name='Лайк')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Оценка комментария'
        verbose_name_plural = 'Оценки комментариев'
        unique_together = ['comment', 'user']


class ContactMessage(models.Model):
    """Модель сообщений обратной связи."""
    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    subject = models.CharField(max_length=200, verbose_name='Тема')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    is_replied = models.BooleanField(default=False, verbose_name='Отвечено')
    admin_notes = models.TextField(blank=True, verbose_name='Заметки администратора')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.subject}'


class SiteSettings(models.Model):
    """Настройки сайта (Singleton)."""
    site_name = models.CharField(max_length=100, default='deev.space', verbose_name='Название сайта')
    site_description = models.TextField(blank=True, verbose_name='Описание сайта')
    owner_name = models.CharField(max_length=200, default='Деев Егор Викторович', verbose_name='Имя владельца')
    owner_title = models.CharField(max_length=200, default='Backend Developer', verbose_name='Должность')
    owner_bio = models.TextField(blank=True, verbose_name='О себе')
    owner_photo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name='Фото владельца')
    owner_email = models.EmailField(default='egor@deev.space', verbose_name='Email')
    owner_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    owner_city = models.CharField(max_length=100, default='Москва', verbose_name='Город')
    telegram_url = models.URLField(blank=True, verbose_name='Telegram')
    github_url = models.URLField(blank=True, verbose_name='GitHub')
    vk_url = models.URLField(blank=True, verbose_name='VKontakte')
    linkedin_url = models.URLField(blank=True, verbose_name='LinkedIn')
    resume_file = models.FileField(upload_to='site/', blank=True, null=True, verbose_name='Файл резюме')
    yandex_metrika_id = models.CharField(max_length=20, blank=True, verbose_name='ID Яндекс.Метрики')
    google_analytics_id = models.CharField(max_length=20, blank=True, verbose_name='ID Google Analytics')

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj