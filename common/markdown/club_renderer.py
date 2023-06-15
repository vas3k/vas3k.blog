import html
import mistune
from urllib.parse import unquote
from slugify import slugify

from common.regexp import IMAGE_RE, VIDEO_RE, YOUTUBE_RE, TWITTER_RE


class Vas3kRenderer(mistune.HTMLRenderer):
    block_counter = 0

    def paragraph(self, text: str) -> str:
        if not text:
            return ""  # hide empty <p></p>
        return super().paragraph(text)

    def heading(self, text, level, **attrs):
        anchor = slugify(text[:24])
        return f"<div class=\"header-{level}\" id=\"{anchor}\"><a href=\"#{anchor}\">{text}</a></div>\n"

    def link(self, text, url, title=None):
        if not text and not title:
            # it's a pure link (without link tag) and we can try to parse it
            embed = self.embed(url, text or "", title or "")
            if embed:
                return embed

        if text is None:
            text = url

        # here's some magic of unescape->unquote->escape
        # to fix cyrillic (and other non-latin) wikipedia URLs
        return f'<a href="{self.safe_url(url)}">{text or url}</a>'

    def image(self, alt, url, title=None):
        embed = self.embed(url, alt, title)
        if embed:
            return embed

        # users can try to "hack" our parser by using non-image urls
        # so, if its not an image or video, display it as a link to avoid auto-loading
        return f'<a href="{mistune.escape(url)}">{mistune.escape(url)}</a>'

    def embed(self, src, alt="", title=None):
        if IMAGE_RE.match(src):
            return self.simple_image(src, alt, title)

        if YOUTUBE_RE.match(src):
            return self.youtube(src, alt, title)

        if VIDEO_RE.match(src):
            return self.video(src, alt, title)

        if TWITTER_RE.match(src):
            return self.tweet(src, alt, title)

        return None

    def simple_image(self, src, alt="", title=None):
        title = title or alt
        image_tag = f'<img src="{mistune.escape(src)}" alt="{mistune.escape(title)}">'
        caption = f"<figcaption>{title}</figcaption>" if title else ""
        return f'<figure>{image_tag}{caption}</figure>'

    def youtube(self, src, alt="", title=None):
        youtube_match = YOUTUBE_RE.match(src)
        playlist = ""
        if youtube_match.group(2):
            playlist = f"list={mistune.escape(youtube_match.group(2))}&listType=playlist&"
        video_tag = (
            f'<span class="ratio-16-9">'
            f'<iframe loading="lazy" src="https://www.youtube.com/embed/{mistune.escape(youtube_match.group(1) or "")}'
            f'?{playlist}autoplay=0&amp;controls=1&amp;showinfo=1&amp;vq=hd1080"'
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"'
            f'allowfullscreen></iframe>'
            f"</span>"
        )
        caption = f"<figcaption>{mistune.escape(title)}</figcaption>" if title else ""
        return f"<figure>{video_tag}{caption}</figure>"

    def video(self, src, alt="", title=None):
        video_tag = (
            f'<video src="{mistune.escape(src)}" controls loop playsinline>{mistune.escape(alt)}</video>'
        )
        caption = f"<figcaption>{mistune.escape(title)}</figcaption>" if title else ""
        return f"<figure>{video_tag}{caption}</figure>"

    def tweet(self, src, alt="", title=None):
        tweet_match = TWITTER_RE.match(src)
        twitter_tag = f'<blockquote class="twitter-tweet" tw-align-center>' \
                      f'<a href="{tweet_match.group(1)}"></a></blockquote><br>' \
                      f'<a href="{src}" target="_blank">{src}</a>'
        return twitter_tag
