__all__ = ["text_block"]

from common.markdown.plugins.utils import parse_classes_and_ids

TEXT_BLOCK_PATTERN = r'\[{3}(?P<text_block_classes>[^\s]+)?(?P<text_block_text>[\s\S]+?)\]{3}'


def parse_text_block(block, m, state):
    text = m.group("text_block_text")
    classes = m.group("text_block_classes")

    child = state.child_state(text)
    block.parse(child)

    state.append_token({"type": "text_block", "children": child.tokens, "attrs": {"classes": classes}})
    return m.end()


def render_text_block(renderer, text, **attrs):
    block_counter = 0
    if hasattr(renderer, "block_counter"):
        renderer.block_counter += 10
        block_counter = renderer.block_counter
    classes, ids = parse_classes_and_ids(attrs.get("classes") or "")
    return f'<div class="block-text {" ".join(classes)}" id="{" ".join(ids)}">' \
           f'{text}' \
           f'<br><br>[commentable {block_counter}]</div>\n'


def text_block(md):
    """
    Custom plugin which supports block-like things:

    [[[
    some text
    ]]]

    They are custom to vas3k blog
    """
    md.block.register("text_block", TEXT_BLOCK_PATTERN, parse_text_block)
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("text_block", render_text_block)
