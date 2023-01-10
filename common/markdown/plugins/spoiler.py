__all__ = ["spoiler"]

SPOILER_BLOCK_PATTERN = r'\[\?(?P<spoiler_text>.+?)\?\]'


def parse_spoiler_block(inline, m, state):
    text = m.group("spoiler_text")

    new_state = state.copy()
    new_state.src = text
    children = inline.render(new_state)

    state.append_token({"type": "spoiler", "children": children})
    return m.end()


def render_spoiler(renderer, text):
    return f"<span class=\"block-spoiler\">" \
           f"<span class=\"block-spoiler-button\">?</span>" \
           f"<span class=\"block-spoiler-text\">{text}</span>" \
           f"</span>\n\n"


def spoiler(md):
    """
    Custom plugin which supports spoilers in text

    Some text [? spoiler ?] other text

    They are custom to vas3k blog
    """
    md.inline.register("spoiler", SPOILER_BLOCK_PATTERN, parse_spoiler_block, before="link")
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("spoiler", render_spoiler)
