from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Project


class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class ProjectSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Project.objects.filter(is_visible=True)

    def location(self, obj):
        return f'/projects/#{obj.slug}'


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['index', 'about', 'projects', 'blog', 'achievements', 'contacts']

    def location(self, item):
        return reverse(item)