__all__ = ["media_block"]

from common.markdown.plugins.utils import parse_classes_and_ids

MEDIA_BLOCK_PATTERN = r'\{{3}(?P<media_block_classes>[^\s]+)?(?P<media_block_text>[\s\S]+?)\}{3}'


def parse_media_block(block, m, state):
    text = m.group("media_block_text")
    classes = m.group("media_block_classes")

    child = state.child_state(text)
    block.parse(child)

    state.append_token({"type": "media_block", "children": child.tokens, "attrs": {"classes": classes}})
    return m.end()


def render_media_block(renderer, text, **attrs):
    text = text.replace("<p>", "").replace("</p>", "")  # dirty hack to fix some browsers
    classes, ids = parse_classes_and_ids(attrs.get("classes") or "")
    return f'<div class="block-media {" ".join(classes)}" id="{" ".join(ids)}">{text}</div>\n'


def media_block(md):
    """
    Custom plugin which supports media-like things:

    {{{
    some text
    }}}

    They are custom to vas3k blog
    """
    md.block.register("media_block", MEDIA_BLOCK_PATTERN, parse_media_block)
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("media_block", render_media_block)
