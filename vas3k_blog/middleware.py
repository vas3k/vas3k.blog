import logging
import time

from django.utils import translation
from django.conf import settings

from utils.request import parse_ip_address

log = logging.getLogger("vas3k_blog.access_log")


class DomainLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get domain from request
        domain = request.get_host().split(':')[0]  # Remove port if present

        # Set language based on domain or default
        language = settings.DOMAIN_LANGUAGES.get(domain)
        request.LANGUAGE_CODE = language if language else settings.LANGUAGE_CODE
        translation.activate(request.LANGUAGE_CODE)

        response = self.get_response(request)

        # Add Content-Language header
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
            f"[{requester_ip}] {method} {domain} {path} {status_code} -> {duration} sec "
            f"UA: {user_agent} Ref: {referer}",
        )

        return response
