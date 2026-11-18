from django.contrib.sitemaps import Sitemap
from django.db.models import Q

from posts.models import Post


class BlogPostsSitemap(Sitemap):
    def items(self):
        return Post.visible_objects().filter(Q(url__isnull=True) | Q(url=""))

    def lastmod(self, obj: Post):
        return obj.updated_at


sitemaps = {
    "posts": BlogPostsSitemap,
}
