import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from premailer import Premailer

from inside.models import Subscriber

log = logging.getLogger(__name__)


def prepare_letter(html, base_url):
    html = Premailer(
        html=html,
        base_url=base_url,
        strip_important=False,
        keep_style_tags=True,
        capitalize_float_margin=True,
        cssutils_logging_level=logging.CRITICAL,
    ).transform()
    if "<!doctype" not in html:
        html = f"<!doctype html>{html}"
    return html


def send_vas3k_email(subscriber: Subscriber, subject: str, html: str, force: bool = False, **kwargs):
    if not subscriber.is_confirmed and not force:
        log.warn(f"Not sending to {subscriber.email}. Not confirmed")

    prepared_html = prepare_letter(html, base_url=f"https://{settings.APP_HOST}")

    email = EmailMultiAlternatives(
        subject=subject,
        body=prepared_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscriber.email],
        headers={
            "List-Unsubscribe": f"https://{settings.APP_HOST}/unsubscribe/{subscriber.secret_hash}/"
        },
        **kwargs
    )
    email.attach_alternative(prepared_html, "text/html")
    email.content_subtype = "html"
    return email.send(fail_silently=True)
