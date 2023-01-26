from django.db.models import F
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from comments.models import Comment
from posts.forms import PostEditForm
from posts.models import Post
from posts.renderers import render_list, render_list_all, render_post
from vas3k_blog.posts import INDEX_PAGE_BEST_POSTS, POST_TYPES


def index(request):
    # blog posts
    blog_posts = Post.visible_objects()\
        .order_by("-created_at")

    return render(request, "index.html", {
        "blocks": [
            {
                "title": "",
                "template": "index/posts2.html",
                "posts": blog_posts
            },
            {
                "title": "About me",
                "template": "index/about.html",
                "posts": []
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
    post = get_object_or_404(Post, slug=post_slug)

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
