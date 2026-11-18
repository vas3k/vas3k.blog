from django.db import IntegrityError, transaction

from posts.models import Post
from translations.ai import language_name, translate_texts
from translations.text import update_post_text
from translations.models import TranslationState
from vas3k_blog.exceptions import TranslationError


TEXT_FIELDS = ("title", "subtitle", "text", "og_title", "og_description", "announce_text")
PUBLICATION_FIELDS = ("published_at", "is_visible", "is_members_only", "is_commentable", "is_visible_on_home_page")
COPY_FIELDS = (
    "slug", "type", "author", "image", "og_image", "data", "css",
    "created_at", "published_at", "is_visible", "is_members_only",
    "is_commentable", "is_visible_on_home_page",
)


def translate_post(source, target_language, draft=False, adopt_existing=False):
    language_name(target_language)

    if not source.id or source._state.adding or source.lang != "ru":
        raise TranslationError("The source must be a saved Russian post.")

    source.refresh_from_db()
    state = TranslationState.objects.get_or_create(source=source, language=target_language)[0]
    try:
        return sync_translation(source, state, draft=draft, adopt_existing=adopt_existing)
    except (TranslationError, IntegrityError) as exc:
        state.pending = True
        state.error = str(exc)
        state.save(update_fields=["pending", "error"])
        raise TranslationError(str(exc)) from exc


def sync_translation(source, state, draft=False, adopt_existing=False):
    if source.lang != "ru" or source.is_raw_html or source.url or not source.text or not source.text.strip():
        raise TranslationError("The source must be a Russian post with local Markdown text.")

    source_fields = {field: getattr(source, field) for field in TEXT_FIELDS}
    target = Post.objects.filter(slug=source.slug, lang=state.language).first()

    if state.target_id and (target is None or target.pk != state.target_id):
        raise TranslationError("The translation was moved or replaced; review its saved baseline.")

    publication_fields = {
        field: getattr(source, field).isoformat() if field == "published_at" and source.published_at else getattr(source, field)
        for field in PUBLICATION_FIELDS
    }
    if target:
        changed = []
        for field in PUBLICATION_FIELDS:
            if state.source_fields.get(field) != publication_fields[field]:
                value = getattr(source, field)
                if getattr(target, field) != value:
                    setattr(target, field, value)
                    changed.append(field)
        if draft:
            target.is_visible = False
            changed.append("is_visible")
        if changed:
            target.save(update_fields=changed)

    current_target = {field: getattr(target, field) for field in TEXT_FIELDS} if target else None

    if adopt_existing:
        if not target:
            raise TranslationError("There is no existing translation to adopt.")
        translated = baseline = current_target
    elif target:
        if not set(TEXT_FIELDS).issubset(state.source_fields) or set(state.target_fields) != set(TEXT_FIELDS):
            raise TranslationError(
                f"Existing {state.language} translation has no baseline. Review it, then run "
                f"translate {source.slug} --lang {state.language} --adopt-existing."
            )
        translated, baseline = update_post_text(
            {field: state.source_fields[field] for field in TEXT_FIELDS},
            source_fields, state.target_fields, current_target, state.language,
        )
    else:
        texts = translate_texts(list(source_fields.values()), state.language)
        translated = baseline = dict(zip(TEXT_FIELDS, texts))

    with transaction.atomic():
        if target:
            changed = [field for field in TEXT_FIELDS if translated[field] != current_target[field]]
            if changed:
                for field in changed:
                    setattr(target, field, translated[field])
                target.save(update_fields=changed)
        else:
            target = Post(
                **{field: getattr(source, field) for field in COPY_FIELDS},
                **translated,
                lang=state.language,
                updated_at=source.updated_at,
            )
            if draft:
                target.is_visible = False
            target.save(force_insert=True)

        state.target = target
        state.source_fields = {**source_fields, **publication_fields}
        state.target_fields = baseline
        state.pending = False
        state.error = ""
        state.save()

    return target
