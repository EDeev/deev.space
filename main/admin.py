import csv
import json

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import (
    CustomUser, Category, Article, ArticleImage, ArticleFile, ArticleLink,
    Project, ProjectStatus, Skill, Comment, ArticleLike, CommentLike,
    ContactMessage, Experience, Education, SiteSettings
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order', 'articles_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def articles_count(self, obj):
        return obj.articles_count
    articles_count.short_description = 'Статей'


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1
    fields = ['image', 'caption', 'order', 'is_inline']
    ordering = ['order']


class ArticleFileInline(admin.TabularInline):
    model = ArticleFile
    extra = 1
    fields = ['file', 'title', 'description', 'order', 'is_inline']
    ordering = ['order']


class ArticleLinkInline(admin.TabularInline):
    model = ArticleLink
    extra = 1
    fields = ['url', 'title', 'description', 'preview_image', 'order', 'is_inline']
    ordering = ['order']
    readonly_fields = []


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'comments_enabled', 'is_achievement', 'views', 'date', 'image_preview']
    list_filter = ['is_published', 'comments_enabled', 'is_achievement', 'category', 'date']
    search_fields = ['title', 'post', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date'
    list_editable = ['is_published', 'comments_enabled']
    readonly_fields = ['views', 'date', 'updated_at', 'image_preview_large', 'likes_summary']
    inlines = [ArticleImageInline, ArticleFileInline, ArticleLinkInline]

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'sub_title', 'excerpt', 'post')
        }),
        ('Превью (обложка)', {
            'fields': ('img', 'show_cover_in_article', 'image_preview_large')
        }),
        ('Галерея изображений', {
            'fields': ('gallery_display_mode',),
            'description': 'Добавьте изображения ниже в инлайн-форме "Изображения статьи"'
        }),
        ('Категоризация', {
            'fields': ('category', 'author')
        }),
        ('Комментарии и медиа', {
            'fields': ('comments_enabled', 'exclude_inline_from_blocks'),
            'description': 'Управление комментариями и отображением медиа-контента'
        }),
        ('Достижение', {
            'fields': ('is_achievement', 'achievement_icon', 'achievement_date'),
            'classes': ('collapse',)
        }),
        ('Публикация', {
            'fields': ('is_published', 'views', 'date', 'updated_at')
        }),
        ('Лайки и дизлайки', {
            'fields': ('likes_summary',),
        }),
    )

    @admin.display(description='Оценки сейчас')
    def likes_summary(self, obj):
        if not obj.pk:
            return '-'
        return (f'лайки: {obj.likes_count}; дизлайки: {obj.dislikes_count}; '
                f'уникальных просмотров: {obj.unique_views.count()}')

    def image_preview(self, obj):
        if obj.img:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.img.url)
        return '-'
    image_preview.short_description = 'Превью'

    def image_preview_large(self, obj):
        if obj.img:
            return format_html('<img src="{}" width="200" style="border-radius: 8px;" />', obj.img.url)
        return 'Нет изображения'
    image_preview_large.short_description = 'Изображение'


@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'is_release', 'order']
    list_editable = ['order', 'is_release']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'card_size', 'languages_short', 'technologies_short', 'show_on_homepage', 'homepage_order', 'order', 'is_visible']
    list_filter = ['status', 'card_size', 'is_visible', 'show_on_homepage']
    search_fields = ['title', 'description', 'technologies', 'programming_languages']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order', 'is_visible', 'card_size', 'status', 'show_on_homepage', 'homepage_order']
    actions = ['export_as_json', 'export_as_csv']

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'short_description', 'description', 'features')
        }),
        ('Визуальное', {
            'fields': ('img_main', 'icon', 'card_size')
        }),
        ('Техническое', {
            'fields': ('programming_languages', 'technologies', 'github_url', 'demo_url'),
            'description': 'Языки программирования и технологии указываются через запятую'
        }),
        ('Статус и отображение', {
            'fields': ('status', 'users_count', 'is_visible', 'order')
        }),
        ('Главная страница', {
            'fields': ('show_on_homepage', 'homepage_order'),
            'description': 'Настройки отображения проекта на главной странице'
        }),
    )

    def languages_short(self, obj):
        langs = obj.get_languages_list()[:2]
        return ', '.join(langs) + ('...' if len(obj.get_languages_list()) > 2 else '') if langs else '-'
    languages_short.short_description = 'Языки'

    def technologies_short(self, obj):
        techs = obj.get_technologies_list()[:3]
        return ', '.join(techs) + ('...' if len(obj.get_technologies_list()) > 3 else '')
    technologies_short.short_description = 'Технологии'

    def _project_row(self, obj):
        return {
            'title': obj.title,
            'slug': obj.slug,
            'short_description': obj.short_description,
            'description': obj.description,
            'features': obj.features,
            'icon': obj.icon,
            'card_size': obj.get_card_size_display(),
            'programming_languages': obj.programming_languages,
            'technologies': obj.technologies,
            'github_url': obj.github_url,
            'demo_url': obj.demo_url,
            'status': obj.status.name if obj.status else '',
            'users_count': obj.users_count,
            'is_visible': obj.is_visible,
            'order': obj.order,
            'show_on_homepage': obj.show_on_homepage,
            'homepage_order': obj.homepage_order,
        }

    def export_as_json(self, request, queryset):
        rows = [self._project_row(obj) for obj in queryset]
        response = HttpResponse(
            json.dumps(rows, ensure_ascii=False, indent=2),
            content_type='application/json; charset=utf-8',
        )
        response['Content-Disposition'] = 'attachment; filename="projects_export.json"'
        return response
    export_as_json.short_description = 'Выгрузить выбранные проекты в JSON'

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="projects_export.csv"'
        fieldnames = list(self._project_row(queryset.first()).keys()) if queryset.exists() else []
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        for obj in queryset:
            writer.writerow(self._project_row(obj))
        return response
    export_as_csv.short_description = 'Выгрузить выбранные проекты в CSV'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'icon', 'order']
    list_filter = ['category']
    list_editable = ['order']
    search_fields = ['name']
    ordering = ['category', 'order']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'start_date', 'end_date', 'is_current', 'duration', 'order']
    list_filter = ['is_current', 'company']
    list_editable = ['order']
    search_fields = ['title', 'company', 'description']
    ordering = ['order', '-start_date']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['institution_short_display', 'degree', 'education_type', 'start_year', 'end_year', 'is_current', 'order']
    list_filter = ['education_type', 'is_current']
    list_editable = ['order']
    search_fields = ['institution', 'degree']
    ordering = ['order', '-start_year']

    def institution_short_display(self, obj):
        return obj.institution_short or obj.institution[:30] + '...'
    institution_short_display.short_description = 'Учреждение'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'content_short', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'user__username', 'article__title']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_comments', 'reject_comments']

    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Содержание'

    def approve_comments(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'Одобрено {count} комментариев')
    approve_comments.short_description = 'Одобрить выбранные комментарии'

    def reject_comments(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'Отклонено {count} комментариев')
    reject_comments.short_description = 'Отклонить выбранные комментарии'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'is_replied', 'created_at']
    list_filter = ['is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    list_editable = ['is_read', 'is_replied']
    ordering = ['-created_at']

    fieldsets = (
        ('Сообщение', {
            'fields': ('name', 'email', 'subject', 'message', 'created_at')
        }),
        ('Статус', {
            'fields': ('is_read', 'is_replied', 'admin_notes')
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основное', {
            'fields': ('site_name', 'site_description')
        }),
        ('Владелец', {
            'fields': ('owner_name', 'owner_title', 'owner_bio', 'owner_photo')
        }),
        ('Контакты', {
            'fields': ('owner_email', 'owner_phone', 'owner_city')
        }),
        ('Социальные сети', {
            'fields': ('telegram_url', 'github_url', 'vk_url', 'linkedin_url')
        }),
        ('Файлы', {
            'fields': ('resume_file',)
        }),
        ('Главная — карточка справа', {
            'fields': ('open_to_work', 'work_format')
        }),
        ('Аналитика', {
            'fields': ('yandex_metrika_id', 'google_analytics_id'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ArticleLike)
admin.site.register(CommentLike)

admin.site.site_header = 'deev.space — Администрирование'
admin.site.site_title = 'deev.space Admin'
admin.site.index_title = 'Панель управления'
