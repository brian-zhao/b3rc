from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed

from .models import Post


class LatestPostsFeed(Feed):
    feed_type        = Rss201rev2Feed
    title            = 'B3RC Blog — Breaking 3 Running Club'
    description      = ('Race recaps, parkrun reports, training updates and club news '
                        'from B3RC — Sydney\'s performance-driven running community.')
    author_name      = 'B3RC'
    author_email     = 'info@b3rc.com.au'
    author_link      = 'https://b3rc.com.au'
    language         = 'en'
    ttl              = 120  # minutes

    def link(self):
        return reverse('blog')

    def feed_url(self):
        return reverse('blog_rss')

    def items(self):
        return Post.objects.filter(status='PUBLISHED').order_by('-published_at')[:20]

    def item_link(self, item):
        return reverse('blog_detail', args=[item.slug])

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_categories(self, item):
        return (item.get_category_display(),)

    def item_author_name(self, item):
        if item.author:
            return item.author.get_full_name() or item.author.email
        return 'B3RC'

    def item_enclosure_url(self, item):
        return item.featured_image.url if item.featured_image else None

    def item_enclosure_length(self, item):
        if item.featured_image:
            try:
                return item.featured_image.size
            except Exception:
                return 0
        return 0

    def item_enclosure_mime_type(self, item):
        if item.featured_image:
            name = item.featured_image.name.lower()
            if name.endswith('.png'):
                return 'image/png'
            if name.endswith('.gif'):
                return 'image/gif'
            return 'image/jpeg'
        return None
