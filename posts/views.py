from django.db.models import F
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from comments.models import Comment
from posts.forms import PostEditForm
from posts.models import Post
from posts.renderers import render_list, render_list_all, render_post
from vas3k_blog.posts import INDEX_PAGE_BEST_POSTS


def index(request):
    # select latest post
    top_post = Post.visible_objects()\
        .filter(is_visible_on_home_page=True)\
        .order_by("-created_at")\
        .first()

    # blog posts
    blog_posts = Post.visible_objects()\
        .filter(type="blog", is_visible_on_home_page=True)\
        .exclude(id=top_post.id if top_post else None)\
        .order_by("-created_at")[:3]

    # travel posts
    latest_world_story = Post.visible_objects()\
        .filter(type="world", is_visible_on_home_page=True)\
        .exclude(id=top_post.id if top_post else None)\
        .order_by("-created_at")\
        .first()
    top_world_posts = Post.visible_objects()\
        .filter(type="world", is_visible_on_home_page=True)\
        .exclude(id__in=[
            top_post.id if top_post else None,
            latest_world_story.id if latest_world_story else None
        ])\
        .order_by("-view_count")[:7]
    world_posts = [latest_world_story] + list(top_world_posts)

    # featured posts
    best_posts = Post.visible_objects()\
        .filter(slug__in=INDEX_PAGE_BEST_POSTS)\
        .order_by("-created_at")[:10]

    # notes
    notes_posts = Post.visible_objects()\
        .filter(type="notes", is_visible_on_home_page=True)\
        .order_by("-created_at")[:11]

    return render(request, "index.html", {
        "blocks": [
            {
                "template": "index/main.html",
                "post": top_post
            },
            {
                "title": "",
                "template": "index/posts3.html",
                "posts": blog_posts
            },
            {
                "title": "Обо мне",
                "template": "index/about.html",
                "posts": []
            },
            {
                "title": "Заметки",
                "url": "/notes/",
                "template": "index/posts4.html",
                "posts": notes_posts
            },
            {
                "title": "Отвратительные путешествия",
                "template": "index/posts3.html",
                "url": "/world/",
                "posts": world_posts
            },
            {
                "title": "Нетленки",
                "template": "index/posts2.html",
                "posts": best_posts
            },
            {
                "title": "Проекты",
                "template": "index/projects.html",
                "posts": []
            }
        ]
    })


def list_posts(request, post_type="all"):
    posts = Post.visible_objects().select_related()

    if post_type and post_type != "all":
        posts = posts.filter(type=post_type)
        if not posts:
            raise Http404()

        return render_list(request, post_type, posts)
    else:
        return render_list_all(request, posts)


def show_post(request, post_type, post_slug):
    post = get_object_or_404(Post, slug=post_slug)

    # post_type can be changed
    if post.type != post_type:
        return redirect("show_post", post.type, post.slug)

    # drafts are visible only to admins
    if not post.is_visible:
        # if not request.me or not request.me.is_admin:
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

    return render_post(request, post, {
        "post": post,
        "comments": comments,
    })


def edit_post(request, post_type, post_slug):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return HttpResponseForbidden()

    post = get_object_or_404(Post, type=post_type, slug=post_slug)

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
