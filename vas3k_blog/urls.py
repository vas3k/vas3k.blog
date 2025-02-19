from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page

from clickers.views import click_comment, click_block
from comments.views import delete_comment, create_comment
from inside.views import donate, subscribe, confirm, unsubscribe
from posts.sitemaps import sitemaps
from posts.views import index, show_post, list_posts, edit_post
from rss.feeds import FullFeed
from users.views import profile, robots
from authn.views import log_in, log_out, login_club, login_patreon, club_callback, patreon_callback

urlpatterns = [
    path("", index, name="index"),

    path(r"godmode/", admin.site.urls),

    path(r"login/", log_in, name="login"),
    path(r"logout/", log_out, name="logout"),
    path(r"auth/login/club/", login_club, name="login_club"),
    path(r"auth/login/patreon/", login_patreon, name="login_patreon"),
    path(r"auth/club_callback/", club_callback, name="club_callback"),
    path(r"auth/patreon_callback/", patreon_callback, name="patreon_callback"),
    path(r"profile/", profile, name="profile"),

    path(r"donate/", donate, name="donate"),
    path(r"subscribe/", subscribe, name="subscribe"),
    path(r"subscribe/confirm/<str:secret_hash>/", confirm, name="subscribe_confirm"),
    path(r"unsubscribe/<str:secret_hash>/", unsubscribe, name="unsubscribe"),

    path(r"rss/", cache_page(60 * 60)(FullFeed()), name="rss.full"),
    path(r"rss/public/", cache_page(60 * 60)(FullFeed()), name="rss.public"),
    path(r"rss/private/", cache_page(60 * 60)(FullFeed()), name="rss.private"),
    path(r"rss/blog/", cache_page(60 * 60)(FullFeed()), name="rss.blog"),  # legacy

    path(r"clickers/comments/<str:comment_id>/", click_comment, name="click_comment"),
    path(r"clickers/blocks/<str:post_slug>/<str:block>/", click_block, name="click_block"),

    path(r"comments/create/", create_comment, name="create_comment"),
    path(r"comments/<str:comment_id>/delete/", delete_comment, name="delete_comment"),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots, name="robots"),

    path(r"<str:post_type>/<str:post_slug>/", show_post, name="show_post"),
    path(r"<str:post_type>/<str:post_slug>/index.html", show_post, name="show_post_legacy"),  # legacy fallback
    path(r"<str:post_type>/<str:post_slug>/edit/", edit_post, name="edit_post"),
    path(
        r"<str:post_type>/<str:post_slug>/<str:block>/",
        RedirectView.as_view(url="/%(post_type)s/%(post_slug)s#%(block)s", permanent=True),
        name="show_post_block"
    ),
    # path(r"<str:type>/<str:slug>/thepub/", show_post, name="story_epub"),
    path(r"<str:post_type>/", list_posts, name="list_posts"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
