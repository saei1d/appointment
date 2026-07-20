from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPage


class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        # Only include published blog pages
        return BlogPage.objects.live().public()

    def location(self, item):
        return reverse('blog:detail', kwargs={'slug': item.slug})

    def lastmod(self, item):
        return item.last_published_at or item.first_published_at
