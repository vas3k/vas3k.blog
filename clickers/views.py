from django.db.models import F
from django.http import Http404, JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import get_object_or_404, render

from clickers.models import Clicker
from comments.models import Comment
from posts.models import Post
from utils.request import parse_ip_address


def click_comment(request, comment_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    comment = get_object_or_404(Comment, id=comment_id)

    clicker, is_created = Clicker.objects.get_or_create(
        post_id=comment.post_id,
        block=comment.id,
        ipaddress=parse_ip_address(request),
        defaults=dict(
            post_id=comment.post_id,
            comment_id=comment.id,
            block=comment.id,
            useragent=request.META.get("HTTP_USER_AGENT", ""),
        )
    )

    if is_created:
        Comment.objects.filter(id=comment.id).update(upvotes=F("upvotes") + 1)
        return HttpResponse(comment.upvotes + 1)

    return HttpResponse(comment.upvotes)


def click_block(request, post_slug, block):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    post = get_object_or_404(Post, slug=post_slug)

    clicker, is_created = Clicker.objects.get_or_create(
        post=post,
        block=block,
        ipaddress=parse_ip_address(request),
        defaults=dict(
            useragent=request.META.get("HTTP_USER_AGENT", ""),
        )
    )

    if is_created:
        total_clicks = Clicker.objects.filter(post=post, block=block).count()
    else:
        total_clicks = "x"

    return render(request, "clickers/clicker.html", {
        "post": post,
        "text": clicker.block or "",
        "block": clicker.block,
        "votes": total_clicks,
        "is_voted": True,
    })
