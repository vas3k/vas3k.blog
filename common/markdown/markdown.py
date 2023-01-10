import mistune

from common.markdown.club_renderer import Vas3kRenderer
from common.markdown.email_renderer import EmailRenderer
from common.markdown.plain_renderer import PlainRenderer
from common.markdown.plugins.cite_block import cite_block
from common.markdown.plugins.media_block import media_block
from common.markdown.plugins.spoiler import spoiler
from common.markdown.plugins.text_block import text_block


def markdown_text(text, renderer=Vas3kRenderer):
    markdown = mistune.create_markdown(
        escape=False,
        hard_wrap=True,
        renderer=renderer(escape=False) if renderer else None,
        plugins=[
            "strikethrough",
            "url",
            "table",
            "speedup",
            text_block,
            media_block,
            spoiler,
            cite_block,
        ]
    )
    return markdown(text)


def markdown_comment(text, renderer=Vas3kRenderer):
    markdown = mistune.create_markdown(
        escape=True,
        hard_wrap=True,
        renderer=renderer(escape=True) if renderer else None,
        plugins=[
            "strikethrough",
            "url",
            "speedup",
        ]
    )
    return markdown(text)


def markdown_plain(text):
    return markdown_text(text, renderer=PlainRenderer)


def markdown_email(text):
    return markdown_text(text, renderer=EmailRenderer)
