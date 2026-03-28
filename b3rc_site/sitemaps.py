from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Post


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    i18n = True

    def items(self):
        return ['home', 'about', 'activities', 'find_us', 'sponsors', 'blog']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'home':
            return 1.0
        if item in ('about', 'activities', 'blog'):
            return 0.8
        return 0.6


class BlogPostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6
    i18n = True

    def items(self):
        return Post.objects.filter(status='PUBLISHED').order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog_detail', args=[obj.slug])
