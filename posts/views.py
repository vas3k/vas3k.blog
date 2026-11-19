from datetime import datetime
from urllib.parse import urlsplit

from django.conf import settings
from django.db.models import F
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _, get_language
from django.utils.http import url_has_allowed_host_and_scheme

from comments.models import Comment
from posts.forms import PostEditForm
from posts.models import Post
from posts.renderers import render_list, render_list_all, render_post
from vas3k_blog.posts import INDEX_PAGE_BEST_POSTS, POST_TYPES


def change_language(request, language):
    if language not in settings.BLOG_EDITIONS:
        raise Http404()

    next_url = request.GET.get("next", "/")
    if not next_url.startswith("/") or not url_has_allowed_host_and_scheme(next_url, allowed_hosts=set()):
        next_url = "/"

    domain = urlsplit("//" + request.get_host()).hostname
    if domain in settings.DOMAIN_LANGUAGES:
        return redirect("https://" + settings.BLOG_EDITIONS[language]["domain"] + next_url)

    response = redirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language, samesite="Lax")
    return response


def index(request):
    visible_posts = Post.visible_objects()

    # select top post
    top_post = visible_posts\
        .filter(is_visible_on_home_page=True)\
        .order_by("-published_at")\
        .first()

    # latest posts
    latest_posts = visible_posts\
        .filter(type__in=["blog", "world"], is_visible_on_home_page=True)\
        .exclude(id=top_post.id if top_post else None)\
        .order_by("-published_at")[:6]

    # travel posts
    latest_world_posts = visible_posts\
        .filter(type="world", is_visible_on_home_page=True)\
        .exclude(id__in=[post.id for post in latest_posts])\
        .exclude(id=top_post.id if top_post else None)\
        .order_by("-published_at")[:3]
    top_world_posts = visible_posts\
        .filter(type="world", is_visible_on_home_page=True)\
        .exclude(id__in=[
            top_post.id if top_post else None,
            *[post.id for post in latest_posts],
            *[post.id for post in latest_world_posts],
        ])\
        .order_by("-view_count")[:5]
    world_posts = list(latest_world_posts) + list(top_world_posts)
    if len(world_posts) < 8:
        world_posts += list(visible_posts
            .filter(type="world", is_visible_on_home_page=True)
            .exclude(id__in=[post.id for post in world_posts])
            .order_by("-published_at")[:8 - len(world_posts)])

    # featured posts
    best_posts = visible_posts\
        .filter(slug__in=INDEX_PAGE_BEST_POSTS)\
        .order_by("-published_at")[:10]

    # notes
    notes_posts = visible_posts\
        .filter(type="notes", is_visible_on_home_page=True)\
        .exclude(id=top_post.id if top_post else None)\
        .order_by("-published_at")[:11]

    return render(request, "index.html", {
        "blocks": [
            {
                "template": "index/main.html",
                "post": top_post
            },
            {
                "title": "",
                "template": "index/posts.html",
                "columns": 3,
                "wide": True,
                "card_template": "posts/cards/horizontal.html",
                "posts": latest_posts
            },
            {
                "title": _("Обо мне"),
                "template": "index/about.html",
                "posts": []
            },
            {
                "title": _("Заметки"),
                "url": "/notes/",
                "template": "index/posts.html",
                "columns": 4,
                "wide": True,
                "card_template": "posts/cards/vertical.html",
                "posts": notes_posts
            },
            {
                "title": _("Отвратительные путешествия"),
                "template": "index/posts.html",
                "columns": 3,
                "wide": True,
                "card_template": "posts/cards/horizontal.html",
                "url": "/world/",
                "posts": world_posts
            },
            {
                "title": _("Нетленки"),
                "template": "index/posts.html",
                "columns": 2,
                "card_template": "posts/cards/horizontal.html",
                "posts": best_posts
            },
            {
                "title": _("Проекты"),
                "template": "index/projects.html",
                "projects": [
                    {
                        "url": "http://vas3k.club/",
                        "image": "https://i.vas3k.ru/235b9705e449cd3c4e0d48ff41fe31196d6cbe359cdbd45e24359ac555fb9a0d.png",
                        "title": _("Вастрик.Клуб"),
                        "subtitle": _("Наше уютное закрытое коммьюнити на краю большого интернета"),
                    },
                    {
                        "url": "https://basa.club/",
                        "image": static("images/logos/basa.png"),
                        "title": "Basa",
                        "subtitle": _("Каталог рекомендаций и объявлений для всех в комьюнити"),
                    },
                    {
                        "url": "https://taxhacker.app/",
                        "image": "https://i.vas3k.blog/5658ab60079563c38b0664abf3d9010cdb1f643ff0f07d11130e9a8e9688ccfb.png",
                        "title": _("TaxHacker"),
                        "subtitle": _("Self-hosted трекер инвойсов и расходов с AI"),
                    },
                    {
                        "url": "https://infomate.club/",
                        "image": "https://i.vas3k.ru/47b9b0180d8eb1a9ee13ed45a0328a11da46661a15a4f813ebe10f106ca559a9.png",
                        "title": _("Infomate"),
                        "subtitle": _("Чтобы оставаться в курсе событий и получать информацию из разных источников"),
                    },
                    {
                        "url": "https://year.vas3k.cloud/",
                        "image": "https://i.vas3k.blog/702946d6657c92e7294a2ff1e8a9d63c5f3acd89cf5cfd77f0ddf7e0312d2e70.jpg",
                        "title": _("Планы на год"),
                        "subtitle": _("Мой личный подход к ежегодному планированию"),
                    },
                ]
            },
        ]
    })


def list_posts(request, post_type="all"):
    posts = Post.visible_objects().select_related()

    if post_type and post_type != "all":
        if post_type not in POST_TYPES:
            raise Http404()

        posts = posts.filter(type=post_type)
        if not posts:
            raise Http404()

        return render_list(request, post_type, posts)
    else:
        return render_list_all(request, posts)


def show_post(request, post_type, post_slug):
    post = get_object_or_404(Post, slug=post_slug, lang=get_language())

    # post_type can be changed
    if post.type != post_type:
        return redirect("show_post", post.type, post.slug)

    # post_type can be removed
    if post_type not in POST_TYPES:
        raise Http404()

    # drafts are visible only with a flag
    if not post.is_visible and not request.GET.get("preview"):
        raise Http404()

    Post.objects.filter(id=post.id)\
        .update(view_count=F("view_count") + 1)

    # don't show private posts into public
    if post.is_members_only:
        if not request.user.is_authenticated:
            return render(request, "users/post_access_denied.html", {
                "post": post
            })

    if post.url:
        return redirect(post.url)

    comments = Comment.visible_objects()\
        .filter(post=post)\
        .order_by("created_at")

    translations = Post.objects.filter(
        lang__in=settings.BLOG_EDITIONS,
        type=post.type,
        slug=post.slug,
        is_visible=True,
        published_at__lte=datetime.utcnow(),
    ).exclude(
        lang=get_language()
    ).order_by("lang")

    translation_source = None
    missing_translations = []
    if request.user.is_superuser:
        translation_source = Post.objects.filter(slug=post.slug, lang="ru", is_raw_html=False).first()
        if translation_source and not translation_source.url and translation_source.text:
            existing_languages = set(Post.objects.filter(slug=post.slug).values_list("lang", flat=True))
            missing_translations = [
                language for language in settings.TRANSLATION_LANGUAGES if language not in existing_languages
            ]

    return render_post(request, post, {
        "post": post,
        "comments": comments,
        "translations": translations,
        "translation_source": translation_source,
        "missing_translations": missing_translations,
    })


def edit_post(request, post_type, post_slug):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return HttpResponseForbidden()

    post = get_object_or_404(Post, type=post_type, slug=post_slug, lang=get_language())

    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("show_post", post_type=post.type, post_slug=post.slug)
    else:
        form = PostEditForm(instance=post)

    return render(request, "posts/edit.html", {
        "form": form,
    })
