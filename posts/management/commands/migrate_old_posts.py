import logging
import json

from django.core.management import BaseCommand
from django.db import connections
from django.utils.html import strip_tags

from posts.models import Post
from vas3k_blog.posts import POST_TYPES

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate posts from old database to the new one"

    def handle(self, *args, **options):
        with connections["old"].cursor() as cursor:
            cursor.execute("select * from stories order by is_visible desc")
            for row in dictfetchall(cursor):
                if row["type"] not in POST_TYPES:
                    self.stdout.write(f"Skipping: {row['type']} {row['slug']}")
                    continue

                if row["type"] == "blog" and row["slug"].isnumeric() and int(row["slug"]) < 70:
                    continue

                self.stdout.write(f"DT: {row['created_at']}")

                row_data = json.loads(row["data"] or "{}") if row["data"] else {}
                post, _ = Post.objects.update_or_create(
                    slug=parse_slug(row),
                    defaults=dict(
                        type=row["type"],
                        author=row["author"],
                        url=row_data.get("url") if row_data else None,
                        title=row["title"],
                        subtitle=row["subtitle"],
                        image=row["image"],
                        og_title=row["title"],
                        og_image=row["preview_image"] or row["image"],
                        og_description=row["preview_text"],
                        announce_text=row["preview_text"],
                        text=parse_text(row),
                        html_cache=row["text_cache"],
                        data=row_data,
                        created_at=row["created_at"],
                        published_at=row["created_at"],
                        updated_at=row["created_at"],
                        word_count=parse_word_count(row),
                        comment_count=row["comments_count"],
                        view_count=row["views_count"],
                        is_raw_html=bool(not row["text"] and row["html"]),
                        is_visible=row["is_visible"],
                        is_members_only=row["is_members_only"],
                        is_commentable=row["is_commentable"],
                        is_visible_on_home_page=row["is_featured"],
                    )
                )
                self.stdout.write(f"Post {post.slug} updated...")

        self.stdout.write("Done 🥙")


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def parse_slug(row):
    return row["slug"] if row["type"] != "gallery" else f"{row['type']}_{row['slug']}"


def parse_text(row):
    text = row["text"]
    if text:
        if not text.strip().startswith("[[[") and not text.startswith("<div"):
            text = f"[[[\n\n{text}\n\n]]]"
    else:
        text = row["html"]
    return text


def parse_word_count(row):
    text = parse_text(row)
    return strip_tags(text).count(" ") if text else 0
