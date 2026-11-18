from datetime import datetime, timedelta
from uuid import UUID

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db.models import Q

from posts.models import Post
from translations.posts import translate_post
from vas3k_blog.exceptions import TranslationError


class Command(BaseCommand):
    help = "Translate changed Russian posts from the last month and retry pending translations. Run weekly."

    def add_arguments(self, parser):
        parser.add_argument("--post-id", type=UUID, help="Synchronize one Russian post after a save.")
        parser.add_argument("--days", type=int, default=30, help="Look back this many days; defaults to 30.")

    def handle(self, *args, **options):
        if options["days"] < 1:
            raise CommandError("--days must be positive.")

        sources = Post.objects.filter(lang="ru", is_raw_html=False).filter(
            Q(url__isnull=True) | Q(url=""),
        ).exclude(text__isnull=True).exclude(text="")

        if options["post_id"]:
            sources = sources.filter(pk=options["post_id"])
        else:
            since = datetime.utcnow() - timedelta(days=options["days"])
            sources = sources.filter(
                Q(updated_at__gte=since) | Q(created_at__gte=since) | Q(translation_states__pending=True),
            ).distinct()

        failures = 0
        for source in sources.iterator():
            for language in settings.TRANSLATION_LANGUAGES:
                try:
                    translate_post(source, language)
                except TranslationError as exc:
                    failures += 1
                    self.stderr.write(f"{source.slug}/{language}: {exc}")

        if failures:
            raise CommandError(f"{failures} translations remain pending. See the errors above.")
        self.stdout.write(self.style.SUCCESS("Translations are up to date."))
