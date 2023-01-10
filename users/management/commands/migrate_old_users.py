import logging

from django.core.management import BaseCommand
from django.db import connections

from users.models import User

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate users from old database to the new one"

    def handle(self, *args, **options):
        with connections["old"].cursor() as cursor:
            cursor.execute("select * from users where email is not null")
            for row in dictfetchall(cursor):
                user, _ = User.objects.update_or_create(
                    email=row["email"],
                    defaults=dict(
                        username=row["name"],
                        patreon_id=row["platform_id"] if row["platform_id"].isnumeric() else None,
                        vas3k_club_slug=row["platform_id"] if not row["platform_id"].isnumeric() else None,
                        avatar=row["avatar"],
                    )
                )
                self.stdout.write(f"User {user.username} updated...")

        self.stdout.write("Done 🥙")


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

