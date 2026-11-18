from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db.models import Q

from posts.models import Post
from vas3k_blog.exceptions import TranslationError
from translations.posts import translate_post


class Command(BaseCommand):
    help = "Create or incrementally update a language edition of a Russian Markdown post."

    def add_arguments(self, parser):
        parser.add_argument("slug", nargs="?", help="Source Russian post slug (not a URL).")
        parser.add_argument("--latest", action="store_true", help="Use the latest published Russian Markdown post.")
        parser.add_argument("--lang", required=True, choices=list(settings.TRANSLATION_LANGUAGES), help="Target language.")
        parser.add_argument("--adopt-existing", action="store_true", help="Record a reviewed existing translation as the baseline without AI calls.")
        parser.add_argument("--draft", action="store_true", help="Create a missing translation hidden; existing visibility is preserved.")

    def handle(self, *args, **options):
        slug, latest, language = options["slug"], options["latest"], options["lang"]

        if bool(slug) == bool(latest):
            raise CommandError("Provide either a post slug or --latest, but not both.")
        try:
            sources = Post.objects.filter(lang="ru")

            if latest:
                source = sources.filter(
                    Q(url__isnull=True) | Q(url=""),
                    is_visible=True,
                    is_raw_html=False,
                    published_at__lte=datetime.utcnow(),
                ).exclude(text__isnull=True).exclude(text="").order_by("-published_at", "-created_at").first()
            else:
                source = sources.filter(slug=slug).first()
            if not source:
                raise CommandError("No matching Russian source post was found.")

            self.stdout.write(f"Translating '{source.slug}' from ru to {language}. This may take several minutes...")
            post = translate_post(source, language, draft=options["draft"], adopt_existing=options["adopt_existing"])
        except TranslationError as exc:
            raise CommandError(str(exc)) from exc

        status = "published" if post.is_published() else "hidden or scheduled"
        self.stdout.write(self.style.SUCCESS(
            f"Synchronized {language} post {post.id} ({status}): https://{post.get_host()}{post.get_absolute_url()}"
        ))
