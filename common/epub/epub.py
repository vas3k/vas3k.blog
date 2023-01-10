import io
import re
import mimetypes
from urllib.parse import urlparse

import requests
from django.template.loader import render_to_string
from ebooklib import epub

from common.markdown.epub import markdown_epub


def generate_epub(story):
    book = epub.EpubBook()

    book.set_identifier("vas3k_ru_{}".format(story.slug))
    book.set_language("ru")
    book.add_author("vas3k.ru")
    book.add_metadata('DC', 'description', story.preview_text or story.subtitle)
    if story.subtitle:
        book.set_title("{}. {}".format(story.title, story.subtitle))
    else:
        book.set_title(story.title)

    if story.book_image:
        book.set_cover("cover.jpg", requests.get(story.book_image).content)
    else:
        book.set_cover("cover.jpg", requests.get(story.image).content)

    css = epub.EpubItem(
        uid="style",
        file_name="styles/index.css",
        media_type="text/css",
        content=render_to_string("epub/style.css")
    )
    book.add_item(css)

    intro = epub.EpubHtml(title=story.title, file_name="title.xhtml", lang="ru")
    intro.content = render_to_string("epub/title.html", {
        "story": story
    })
    book.add_item(intro)
    spine = [intro]

    xhtml = markdown_epub(story.text)
    xhtml = bundle_images(from_text=xhtml, book=book)

    for index, content in break_pages(xhtml):
        if not content:
            continue

        chapter = epub.EpubHtml(
            uid="chap_{}".format(index),
            title=story.title,
            file_name="chap_{}.xhtml".format(index),
            lang="ru"
        )
        chapter.content = content
        chapter.add_item(css)
        book.add_item(chapter)
        spine.append(chapter)

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # create spine (required for epub)
    book.spine = spine

    mem_file = io.BytesIO()
    epub.write_epub(mem_file, book, {})
    return mem_file.getvalue()


def bundle_images(from_text, book):
    pattern = r"<!--BUNDLE\[(.*?)\]-->"
    images = re.findall(pattern, from_text)
    for image in set(list(images)):
        if "youtu" in image:
            continue

        file_name = image[image.rfind("/") + 1:]
        file_type = guess_mimetype(file_name)
        content = requests.get(image).content
        book.add_item(
            epub.EpubItem(
                uid=file_name,
                file_name="images/{}".format(file_name),
                media_type=file_type,
                content=content
            )
        )
        from_text = from_text.replace(image, "images/{}".format(file_name))

    return from_text


def guess_mimetype(file_name):
    mime, _ = mimetypes.guess_type(file_name)
    if not mime:
        path = urlparse(file_name).path
        mime, _ = mimetypes.guess_type(path or "")
        if not mime:
            mime = "application/octet-stream"
    return mime


def break_pages(text):
    return enumerate(text.split("<!--PAGEBREAK-->"))
