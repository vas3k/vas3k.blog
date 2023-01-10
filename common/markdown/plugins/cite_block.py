__all__ = ["cite_block"]

from common.markdown.plugins.utils import parse_classes

CITE_BLOCK_PATTERN = r'^\% (?P<cite_block_text>[\s\S]+?)$'


def parse_cite_block(block, m, state):
    text = m.group("cite_block_text")

    child = state.child_state(text)
    block.parse(child)

    state.append_token({"type": "cite_block", "children": child.tokens})
    return m.end()


def render_cite_block(renderer, text, **attrs):
    return f'<div class="block-cite">{text}</div>\n'


def cite_block(md):
    """
    Custom plugin which supports block-like things:

    % some text

    They are custom to vas3k blog
    """
    md.block.register("cite_block", CITE_BLOCK_PATTERN, parse_cite_block)
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("cite_block", render_cite_block)
