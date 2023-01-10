from django.db.models import Count
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from clickers.models import Clicker
from posts.models import Post
from utils.request import parse_ip_address
from vas3k_blog.posts import DEFAULT_LIST_ITEMS_PER_PAGE, PostTypeConfig, post_config_by_type


def render_list(request, post_type, posts, context=None):
    context = context or {}
    post_type_config = post_config_by_type(post_type)

    paginator = Paginator(posts, post_type_config.list_items_per_page)
    try:
        posts = paginator.page(request.GET.get("page"))
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, post_type_config.list_template, {
        **context,
        "post_type_config": post_type_config,
        "posts": posts,
    })


def render_list_all(request, posts, context=None):
    paginator = Paginator(posts, DEFAULT_LIST_ITEMS_PER_PAGE * 2)
    try:
        posts = paginator.page(request.GET.get("page"))
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = context or {}
    current_post_template = post_config_by_type(posts[0].type).card_template
    stack = []
    result = []

    for post in posts:
        this_post_template = post_config_by_type(post.type).card_template

        if this_post_template != current_post_template and stack:
            result += [(current_post_template, stack)]
            stack = []
            current_post_template = this_post_template

        stack.append(post)

    if stack:
        result += [(current_post_template, stack)]

    context["post_blocks"] = result

    return render(request, "posts/lists/all.html", {
        **context,
        "post_type_config": PostTypeConfig(),
        "posts": posts,
    })


def render_post(request, post, context=None):
    related = Post.visible_objects()\
        .filter(type=post.type)\
        .exclude(id=post.id)\
        .order_by("-created_at")[:3]

    clickers = {
        c["block"]: {"total": c["total"]}
        for c in Clicker.objects
        .filter(post=post)
        .values("block")
        .annotate(total=Count("block"))
    }

    user_votes = set(
        Clicker.objects
        .filter(post=post, ipaddress=parse_ip_address(request))
        .all().values_list("block", flat=True)
    )

    return render(request, post_config_by_type(post.type).show_template, {
        **context,
        "related": related,
        "clickers": clickers,
        "user_votes": user_votes,
    })
