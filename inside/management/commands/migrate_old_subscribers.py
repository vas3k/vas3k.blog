import logging

from django.core.management import BaseCommand
from django.db import connections, IntegrityError

from inside.models import Subscriber

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate subscribers from old database to the new one"

    def handle(self, *args, **options):
        with connections["old"].cursor() as cursor:
            cursor.execute(
                "select * from subscribers"
            )
            for row in dictfetchall(cursor):
                try:
                    subscriber, _ = Subscriber.objects.update_or_create(
                        email=row["email"],
                        defaults=dict(
                            secret_hash=row["secret_hash"],
                            bounces=row["bounces"],
                            data=row["data"],
                            is_confirmed=row["is_confirmed"],
                            created_at=row["created_at"],
                        )
                    )
                    subscriber.created_at = row["created_at"]  # override django's auto_now=True
                    subscriber.save()
                except IntegrityError:
                    continue

                self.stdout.write(f"Subscriber {subscriber.email} imported...")

        self.stdout.write("Done 🥙")


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
