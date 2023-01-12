import re

from django import template
from django.conf import settings
from django.template import loader
from django.utils.safestring import mark_safe

from common.markdown.markdown import markdown_text

register = template.Library()
clicker_template = loader.get_template("clickers/clicker.html")
inline_comments_template = loader.get_template("comments/inline-comment-list.html")


@register.simple_tag(takes_context=True)
def show_post(context, post):
    if post.is_raw_html:
        html = post.text or post.html_cache
    else:
        if not post.html_cache or settings.DEBUG:
            new_html = markdown_text(post.text)
            if new_html != post.html_cache:
                # to not flood into history
                post.html_cache = new_html
                post.save(flush_cache=False)
        html = post.html_cache or ""

    html = re.sub(r"\[commentable (.+?)\]", lambda match: commentable(context, match.group(1)), html)
    html = re.sub(r"\[clicker (.+?)\]", lambda match: clicker(context, match.group(1), match.group(1)), html)

    return mark_safe(html)

    # # remove extra blocks for unauthorized users
    # if settings.EXTRA_BLOCK_CLASS in text and not context["me"]:
    #     soup = BeautifulSoup(text, "html.parser")
    #     for block in soup.select("." + settings.EXTRA_BLOCK_CLASS):
    #         block.string = ""
    #         block["class"] = block.get("class", []) + ["block-extra-placeholder"]
    #         block.append(BeautifulSoup(block_placeholder_template.render({"story": post}), "html.parser"))
    #     text = str(soup)


def clicker(context, block, text=None):
    clicker = context["clickers"].get(block) or {}

    return clicker_template.render({
        **context.flatten(),
        "text": text or "",
        "block": block,
        "votes": clicker.get("total") or 0,
        "is_voted": block in context["user_votes"],
    })


def commentable(context, block):
    return inline_comments_template.render({
        **context.flatten(),
        "username": context["cookies"].get("username") or "",
        "block": block,
        "block_comments": [c for c in context["comments"] if str(c.block) == str(block)],
    })


def replace_host_if_mirror(request, text):
    if request.get_host() in settings.MIRRORS:
        text = text.replace(settings.APP_HOST, request.get_host())
    return text
