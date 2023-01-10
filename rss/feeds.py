from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords, truncatechars
from django.utils.html import strip_tags

from posts.models import Post
from django.conf import settings


class FullFeed(Feed):
    title = "Вастрик.ру"
    link = "/rss/"
    description = settings.DESCRIPTION
    hide_members_posts = True

    def items(self):
        items = Post.visible_objects().\
            filter(is_visible_on_home_page=True).\
            order_by("-created_at").\
            select_related()[:30]
        return items

    def item_title(self, item):
        return item.title

    def author_name(self):
        return "Вастрик"

    def item_copyright(self):
        return "vas3k.ru"

    def item_pubdate(self, item):
        return item.created_at

    def item_description(self, item):
        url = item.get_absolute_url()

        result = ""
        if item.image:
            result += f"<a href='{url}'><img src='{item.image}'></a><br><br>"

        if item.og_description:
            result += item.og_description
        else:
            result += truncatechars(strip_tags(item.html_cache or item.text or ""), 400)

        return result


class PrivateFeed(FullFeed):
    title = "Вастрик.ру: Секретный фид"
    link = "/rss/private/"
    hide_members_posts = False


class PublicFeed(FullFeed):
    title = "Вастрик.ру: Только публичные посты"
    link = "/rss/public/"
    hide_members_posts = True

    def items(self):
        items = Post.visible_objects().\
            filter(is_visible_on_home_page=True, is_members_only=False).\
            order_by("-created_at").\
            select_related()[:20]
        return items
