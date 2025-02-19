import vas3k_blog.strings as strings
from django.conf import settings


def settings_processor(request):
    return {
        "settings": settings
    }


def cookies_processor(request):
    return {
        "cookies": request.COOKIES
    }


def strings_processor(request):
    return {
        "strings": strings
    }
