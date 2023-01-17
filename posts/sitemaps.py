from django.contrib.sitemaps import Sitemap

from posts.models import Post


class BlogPostsSitemap(Sitemap):
    def items(self):
        return Post.visible_objects()

    def lastmod(self, obj: Post):
        return obj.updated_at


sitemaps = {
    "posts": BlogPostsSitemap,
}
