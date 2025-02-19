import logging
import time

from django.utils import translation
from django.conf import settings

logger = logging.getLogger("django.full_request")


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
        requester_ip = self.get_client_ip(request)
        status_code = response.status_code
        method = request.method
        path = request.path
        referer = request.META.get("HTTP_REFERER", "-")
        user_agent = request.META.get("HTTP_USER_AGENT", "-")

        # Log the request with additional headers
        logger.info(
            "",
            extra={
                "domain": domain,
                "requester_ip": requester_ip,
                "status_code": status_code,
                "method": method,
                "path": path,
                "duration": duration,
                "referer": referer,
                "user_agent": user_agent,
            },
        )

        return response

    def get_client_ip(self, request):
        """Get real client IP, respecting X-Forwarded-For if present."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]  # First IP in the list
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
