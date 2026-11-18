import logging
import time
from urllib.parse import urlsplit

from django.utils import translation
from django.conf import settings

from utils.request import parse_ip_address

log = logging.getLogger("vas3k_blog.access_log")


class DomainLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = urlsplit("//" + request.get_host()).hostname
        language = settings.DOMAIN_LANGUAGES.get(domain)
        if language:
            request.LANGUAGE_CODE = language
            translation.activate(language)

        response = self.get_response(request)

        if hasattr(request, 'LANGUAGE_CODE'):
            response['Content-Language'] = request.LANGUAGE_CODE

        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        domain = request.get_host()
        requester_ip = parse_ip_address(request)
        status_code = response.status_code
        method = request.method
        path = request.path
        referer = request.META.get("HTTP_REFERER", "-")
        user_agent = request.META.get("HTTP_USER_AGENT", "-")

        log.info(
            f"[{requester_ip}] {method} https://{domain}{path} {status_code} -> {duration:.3f} sec "
            f"Browser: {user_agent} Ref: {referer}",
        )

        return response
