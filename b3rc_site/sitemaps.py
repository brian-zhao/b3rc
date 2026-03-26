from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    i18n = True

    def items(self):
        return ['home', 'about', 'activities', 'find_us', 'sponsors']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'home':
            return 1.0
        if item in ('about', 'activities'):
            return 0.8
        return 0.6
