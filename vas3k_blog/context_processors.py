from django.conf import settings


def settings_processor(request):
    return {
        "settings": settings
    }


def cookies_processor(request):
    return {
        "cookies": request.COOKIES
    }
