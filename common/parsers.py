import re
import requests
from bs4 import BeautifulSoup

TAGS = {
    "title": "title"
}
OG_TAGS = {
    "og:image": "image",
    "og:title": "title",
    "og:description": "description",
    "og:url": "url"
}
TWITTER_TAGS = {
    "twitter:image": "image",
    "twitter:image:src": "image",
    "twitter:title": "title",
    "twitter:description": "description",
    "twitter:url": "url"
}
USERAGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) " \
            "Chrome/41.0.2228.0 Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


def parse_metatags(url):
    try:
        page = requests.get(url, headers={"User-Agent": USERAGENT}, timeout=5.0)
    except:
        return {}

    if not page.headers.get("Content-Type", "").startswith("text/html"):
        return {}

    document = BeautifulSoup(page.text, "html.parser")
    metadata = {
        "title": document.title.string
    }

    for meta in document.html.head.findAll(property=re.compile(r'^twitter')):
        meta_property = meta.get("property")
        if meta_property and meta_property in TWITTER_TAGS:
            meta_content = meta.get("content")
            if meta_content:
                metadata[TWITTER_TAGS[meta_property]] = meta_content

    for meta in document.html.head.findAll(property=re.compile(r'^og')):
        meta_property = meta.get("property")
        if meta_property and meta_property in OG_TAGS:
            meta_content = meta.get("content")
            if meta_content:
                metadata[OG_TAGS[meta_property]] = meta_content

    return metadata
