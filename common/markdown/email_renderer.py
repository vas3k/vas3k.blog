import mistune

from common.markdown.club_renderer import Vas3kRenderer
from common.regexp import YOUTUBE_RE


class EmailRenderer(Vas3kRenderer):
    def simple_image(self, src, alt="", title=None):
        return f"""<img src="{src}" alt="{alt}" width="600" border="0"><br>{title or ""}"""

    def youtube(self, src, alt="", title=None):
        youtube_match = YOUTUBE_RE.match(src)
        youtube_id = mistune.escape(youtube_match.group(1) or "")
        return f'<a href="{mistune.escape(src)}"><span class="ratio-16-9 video-preview" ' \
               f'style="background-image: url(\'https://img.youtube.com/vi/{mistune.escape(youtube_id)}/0.jpg\');">' \
               f'</span></a><br>{mistune.escape(title or "")}'

    def video(self, src, alt="", title=None):
        return f'<video src="{mistune.escape(src)}" controls autoplay loop muted playsinline>{alt}</video><br>{title or ""}'

    def tweet(self, src, alt="", title=None):
        return f'<a href="{mistune.escape(src)}">{mistune.escape(src)}</a><br>{mistune.escape(title or "")}'

    def heading(self, text, level, **attrs):
        tag = f"h{level}"
        return f"<{tag}>{text}</{tag}>\n"
