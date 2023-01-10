DEFAULT_ALLOWED = ["ru", "en"]
DEFAULT = "en"


def request_language(request, allowed=DEFAULT_ALLOWED, default=DEFAULT):
    for locale in allowed:
        if locale in request.GET:
            return locale

    header = request.META.get("HTTP_ACCEPT_LANGUAGE", "")  # e.g. en-gb,en;q=0.8,es-es;q=0.5,eu;q=0.3
    for locale in header.split(","):
        try:
            locale = locale.lower()
            locale = locale.split(";")[0].lower()[:2]
        except (KeyError, ValueError):
            continue
        else:
            if locale in allowed:
                return locale
    return default
