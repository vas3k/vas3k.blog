from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from comments.forms import CommentForm
from comments.models import Comment
from posts.models import Post
from utils.request import parse_ip_address


def create_comment(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    form = CommentForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("post_slug is required")

    post = get_object_or_404(Post, slug=form.cleaned_data.get("post_slug"))
    if not post.is_commentable:
        return render(
            request, "error.html", {
                "message": "Нельзя комментировать этот пост"
            }
        )

    ipaddress = parse_ip_address(request)
    same_ip_comments_24h = Comment.objects.filter(
        ipaddress=ipaddress,
        created_at__gte=datetime.utcnow() - timedelta(hours=24)
    ).count()
    if same_ip_comments_24h >= settings.MAX_COMMENTS_PER_24H:
        return HttpResponseBadRequest(
            "Вы оставили слишком много комментариев, остановитесь"
        )

    comment = Comment.objects.create(
        author=request.user,
        author_name=request.user.username,
        post=post,
        block=form.cleaned_data.get("block"),
        text=form.cleaned_data.get("text"),
        created_at=datetime.utcnow(),
    )

    Post.objects.filter(id=post.id).update(
        comment_count=Comment.objects.filter(post=post, is_visible=True, is_deleted=False).count()
    )

    if comment.block:
        response_template = "comments/partials/create-inline-comment-response.html"
    else:
        response_template = "comments/partials/create-comment-response.html"

    return render(request, response_template, {
        "post": post,
        "comment": comment,
        "block": comment.block,
    })


def delete_comment(request, comment_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not request.user.is_superuser:
        return HttpResponseForbidden()

    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()

    return HttpResponse("☠️ Комментарий удален")
