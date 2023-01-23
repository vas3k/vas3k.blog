import logging
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.template import loader

from inside.models import Subscriber
from inside.senders.email import send_vas3k_email
from posts.models import Post

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send new post announcement via email"

    def add_arguments(self, parser):
        parser.add_argument("--production", type=bool, required=False, default=False)
        parser.add_argument("--hours", type=int, required=False, default=24)
        parser.add_argument("--auto-confirm", type=bool, required=False, default=False)

    def handle(self, *args, **options):
        production = options.get("production")
        hours = options.get("hours") or 24
        if not production:
            hours = 99999

        # Step 1. Check for a new post
        post = Post.objects.filter(
            is_visible=True,
            created_at__lte=datetime.utcnow(),
            created_at__gte=datetime.utcnow() - timedelta(hours=hours),
        ).order_by("-created_at").first()

        if not post:
            self.stdout.write(f"No new posts. Exiting...")
            return

        # Step 2. Select all confirmed subscribers
        if production:
            subscribers = Subscriber.objects.filter(is_confirmed=True).all()
        else:
            subscribers = Subscriber.objects.filter(email="me@vas3k.ru").all()

        # Step 3. Confirm
        auto_confirm = options.get("auto_confirm")
        if not auto_confirm:
            confirm = input(f"Confirm sending new post '{post.title}' to {len(subscribers)} subscribers? [y/N]: ")
            if confirm != "y":
                self.stdout.write(f"Not confirmed. Exiting...")
                return

        # Step 4. Load newsletter template
        new_post_template = loader.get_template("emails/new_post.html")

        # Step 3. Send emails
        for subscriber in subscribers:
            self.stdout.write(f"Generating newsletter for user: {subscriber.email}")

            # render user digest email
            html = new_post_template.render({
                "post": post,
                "subscriber": subscriber,
            })

            # send a letter
            try:
                send_vas3k_email(
                    subscriber=subscriber,
                    subject=f"Новый пост в блоге Вастрика: {post.title}",
                    html=html
                )
            except Exception as ex:
                self.stdout.write(f"Sending to {subscriber.email} failed: {ex}")
                continue

        self.stdout.write("Done 🥙")
