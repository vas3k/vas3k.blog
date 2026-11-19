import json
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db import transaction

from common.markdown.markdown import markdown_text
from posts.models import Post
from translations.ai import translate_texts
from translations.models import TranslationState
from vas3k_blog.exceptions import TranslationError


class Command(BaseCommand):
    help = "One-time repair of untranslated Russian image captions without retranslating articles."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--backup", default="/tmp/image-caption-repair.jsonl")

    def handle(self, *args, **options):
        failures = 0
        for post in Post.objects.filter(lang__in=settings.TRANSLATION_LANGUAGES, is_raw_html=False).iterator():
            lines = (post.text or "").splitlines(keepends=True)
            captions = []
            for line in dict.fromkeys(lines):
                if "![" not in line:
                    continue
                tokens = list(markdown_text(line, renderer=None))
                while tokens:
                    token = tokens.pop()
                    tokens.extend(token.get("children", []))
                    if token["type"] != "image":
                        continue
                    caption = token.get("attrs", {}).get("title") or ""
                    children = list(token.get("children", []))
                    while children:
                        child = children.pop()
                        caption += child.get("raw", "")
                        children.extend(child.get("children", []))
                    if any("\u0400" <= char <= "\u04ff" for char in caption):
                        captions.append(line)
                        break

            if not captions:
                continue
            self.stdout.write(f"{post.slug}/{post.lang}: {len(captions)} caption lines")
            if not options["apply"]:
                continue

            try:
                translated = translate_texts(captions, post.lang, context={
                    "title": post.title,
                    "task": "Repair untranslated image captions. Translate image alt text and titles; preserve URLs and all surrounding text exactly.",
                })
            except TranslationError as exc:
                failures += 1
                self.stderr.write(f"{post.slug}/{post.lang}: {exc}")
                continue

            replacements = dict(zip(captions, translated))
            text = "".join(replacements.get(line, line) for line in lines)
            with transaction.atomic():
                states = list(TranslationState.objects.filter(target=post))
                with Path(options["backup"]).open("a", encoding="utf-8") as backup:
                    backup.write(json.dumps({
                        "post_id": str(post.pk), "slug": post.slug, "lang": post.lang, "text": post.text,
                        "states": [{"id": state.pk, "target_fields": state.target_fields} for state in states],
                    }, ensure_ascii=False) + "\n")
                changed = Post.objects.filter(pk=post.pk, text=post.text).update(
                    text=text, html_cache=None, updated_at=datetime.utcnow(),
                )
                if not changed:
                    failures += 1
                    self.stderr.write(f"{post.slug}/{post.lang}: changed during repair; skipped")
                    continue
                for state in states:
                    baseline = state.target_fields.get("text")
                    if baseline is not None:
                        state.target_fields["text"] = "".join(
                            replacements.get(line, line) for line in baseline.splitlines(keepends=True)
                        )
                        state.save(update_fields=["target_fields"])
            self.stdout.write(f"Repaired {post.slug}/{post.lang}")

        if failures:
            raise CommandError(f"{failures} caption repairs failed; see the log above.")
