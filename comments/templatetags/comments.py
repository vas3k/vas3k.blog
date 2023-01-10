from django import template
from django.utils.safestring import mark_safe

from common.markdown.markdown import markdown_comment

register = template.Library()


@register.simple_tag(takes_context=True)
def show_comment(context, comment):
    return mark_safe(markdown_comment(comment.text))


@register.simple_tag(takes_context=True)
def mark_if_voted(context, comment, css_class, other_css_class="", ipaddress=None):
    user_votes = context.get("user_votes")
    if user_votes:
        return css_class if str(comment.id) in user_votes else other_css_class
    else:
        return other_css_class


@register.filter(is_safe=True)
def without_inline_comments(comments):
    return [c for c in comments if not c.block]
