from django.utils import translation
from django.conf import settings


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
