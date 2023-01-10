import logging

from django.core.management import BaseCommand
from django.db import connections, IntegrityError

from clickers.models import Clicker
from posts.models import Post

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate clickers from old database to the new one"

    def handle(self, *args, **options):
        with connections["old"].cursor() as cursor:
            cursor.execute(
                "select *, (select type from stories where clickers.story_id = stories.id) as post_type, "
                "(select slug from stories where clickers.story_id = stories.id) as post_slug from clickers"
            )
            for row in dictfetchall(cursor):
                post = Post.objects.filter(slug=row["post_slug"], type=row["post_type"]).first()
                if not post:
                    continue

                try:
                    clicker, _ = Clicker.objects.update_or_create(
                        post_id=post.id,
                        comment_id=row["comment_id"],
                        block=row["block"],
                        ipaddress=row["ip"],
                        defaults=dict(
                            created_at=row["created_at"],
                            useragent=row["useragent"],
                        )
                    )
                except IntegrityError:
                    continue

                self.stdout.write(f"Clicker {clicker.id} updated...")

        self.stdout.write("Done 🥙")


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
