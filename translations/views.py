import logging
import subprocess
import sys

from django.conf import settings
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _

from posts.models import Post


logger = logging.getLogger(__name__)


@require_POST
def start_translation(request, post_id, language):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden()

    if language not in settings.TRANSLATION_LANGUAGES:
        raise Http404()

    source = get_object_or_404(Post, pk=post_id, lang="ru", is_raw_html=False)
    if source.url or not source.text or not source.text.strip():
        raise Http404()

    if Post.objects.filter(slug=source.slug, lang=language).exists():
        return render(request, "message.html", {
            "title": _("Перевод уже существует"),
            "message": _("Для этого языка уже есть перевод, возможно, он пока не опубликован."),
        })

    if not settings.OPENAI_API_KEY:
        return render(request, "message.html", {
            "title": _("Перевод не запущен"),
            "message": _("На сервере не настроен ключ OpenAI."),
        }, status=503)

    try:
        subprocess.Popen(
            [sys.executable, str(settings.BASE_DIR / "manage.py"), "translate", source.slug, "--lang", language],
            cwd=settings.BASE_DIR,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        logger.exception("Could not start translation for %s into %s", source.pk, language)
        return render(request, "message.html", {
            "title": _("Перевод не запущен"),
            "message": _("Не удалось запустить процесс перевода. Попробуйте позже."),
        }, status=503)

    return render(request, "message.html", {
        "title": _("Перевод запущен"),
        "message": _("Перевод на %(language)s работает в фоне. Можно закрыть эту страницу: перевод появится в посте, когда будет готов.") % {"language": language.upper()},
    })
