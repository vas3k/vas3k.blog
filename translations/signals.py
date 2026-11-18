import logging
import subprocess
import sys

from django.conf import settings
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from posts.models import Post
from translations.models import TranslationState
from translations.posts import PUBLICATION_FIELDS, TEXT_FIELDS


logger = logging.getLogger(__name__)


def launch_translation(post_id):
    if not settings.OPENAI_API_KEY:
        logger.warning("Translation remains pending for %s: OPENAI_API_KEY is not configured", post_id)
        return

    try:
        subprocess.Popen(
            [sys.executable, str(settings.BASE_DIR / "manage.py"), "sync_translations", "--post-id", str(post_id)],
            cwd=settings.BASE_DIR,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        logger.exception("Could not start translation for %s; it remains pending", post_id)


@receiver(pre_save, sender=Post)
def remember_source(sender, instance, raw=False, using="default", update_fields=None, **kwargs):
    instance.translation_changed = False
    instance.translation_publication_changes = {}

    if raw or instance.lang != "ru":
        return

    watched_fields = {*TEXT_FIELDS, *PUBLICATION_FIELDS, "lang", "is_raw_html", "url"}
    if update_fields is not None and not watched_fields.intersection(update_fields):
        return

    previous = sender.objects.using(using).filter(pk=instance.pk).values(*watched_fields).first()
    changed_fields = watched_fields if update_fields is None else watched_fields.intersection(update_fields)
    instance.translation_publication_changes = {
        field: getattr(instance, field) for field in PUBLICATION_FIELDS
        if field in changed_fields and (previous is None or previous[field] != getattr(instance, field))
    }
    instance.translation_changed = previous is None or any(
        previous[field] != getattr(instance, field) for field in changed_fields
    )


@receiver(post_save, sender=Post)
def schedule_translation(sender, instance, raw=False, using="default", **kwargs):
    if raw or instance.lang != "ru":
        return

    publication_changes = getattr(instance, "translation_publication_changes", {})
    if publication_changes:
        Post.objects.using(using).filter(
            slug=instance.slug, type=instance.type, lang__in=settings.TRANSLATION_LANGUAGES,
        ).update(**publication_changes, updated_at=instance.updated_at)

    if instance.is_raw_html or instance.url or not instance.text:
        return

    if not getattr(instance, "translation_changed", False):
        return

    for language in settings.TRANSLATION_LANGUAGES:
        TranslationState.objects.using(using).update_or_create(
            source=instance, language=language, defaults={"pending": True, "error": ""},
        )

    transaction.on_commit(lambda: launch_translation(instance.pk), using=using, robust=True)
