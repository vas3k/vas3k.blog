import logging

from django.core.management import BaseCommand
from django.db import connections

from comments.models import Comment
from posts.models import Post
from users.models import User

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate comments from old database to the new one"

    def handle(self, *args, **options):
        with connections["old"].cursor() as cursor:
            cursor.execute(
                "select *, (select type from stories where comments.story_id = stories.id) as post_type, "
                "(select slug from stories where comments.story_id = stories.id) as post_slug from comments"
            )
            for row in dictfetchall(cursor):
                post = Post.objects.filter(slug=row["post_slug"], type=row["post_type"]).first()
                if not post:
                    continue

                user = None
                if row["user_id"]:
                    cursor.execute("select * from users where id = %s", [row["user_id"]])
                    old_user = dictfetchall(cursor)
                    if old_user:
                        old_user = old_user.pop()
                        old_user_email = old_user["email"] or old_user["name"] + "@legacy.vas3k.ru"
                        user, _ = User.objects.get_or_create(
                            email=old_user_email,
                            defaults=dict(
                                username=old_user["name"],
                                patreon_id=old_user["platform_id"] if old_user["platform_id"].isnumeric() else None,
                                vas3k_club_slug=old_user["platform_id"] if not old_user["platform_id"].isnumeric() else None,
                                avatar=old_user["avatar"],
                            )
                        )

                comment, _ = Comment.objects.update_or_create(
                    id=row["id"],
                    defaults=dict(
                        author_id=user.id if user else None,
                        author_name=row["author"],
                        post_id=post.id,
                        text=row["text"],
                        block=row["block"],
                        metadata=row["data"],
                        ipaddress=row["ip"],
                        useragent=row["useragent"],
                        created_at=row["created_at"],
                        updated_at=row["created_at"],
                        upvotes=row["rating"],
                        is_visible=row["is_visible"],
                        is_deleted=False,
                        is_pinned=False,
                    )
                )
                self.stdout.write(f"Comment {comment.id} updated...")

        self.stdout.write("Done 🥙")


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
