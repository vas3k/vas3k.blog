import os
from pathlib import Path
from random import randint

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY") or "wow so secret"
DEBUG = (os.getenv("DEBUG") != "false")

ALLOWED_HOSTS = ["0.0.0.0", "127.0.0.1", "vas3k.blog", "vas3k.ru"]
INTERNAL_IPS = ["127.0.0.1"]

ADMINS = [
    ("vas3k", "me@vas3k.ru"),
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "authn.apps.AuthnConfig",
    "users.apps.UsersConfig",
    "posts.apps.PostsConfig",
    "comments.apps.CommentsConfig",
    "rss.apps.RssConfig",
    "inside.apps.InsideConfig",
    "clickers.apps.ClickersConfig",
    "notifications.apps.NotificationsConfig",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vas3k_blog.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "frontend/html",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "vas3k_blog.context_processors.settings_processor",
                "vas3k_blog.context_processors.cookies_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "vas3k_blog.wsgi.application"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler"
        },
    },
    "loggers": {
        "": {  # "catch all" loggers by referencing it with the empty string
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB") or "vas3k_blog",
        "USER": os.getenv("POSTGRES_USER") or "postgres",
        "PASSWORD": os.getenv("POSTGRES_PASSWORD") or "",
        "HOST": os.getenv("POSTGRES_HOST") or "localhost",
        "PORT": os.getenv("POSTGRES_PORT") or 5432,
    }
}

MIGRATE = os.getenv("MIGRATE")
if MIGRATE:
    DATABASES.update({
        "old": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.getenv("MIGRATE"),
            "USER": os.getenv("POSTGRES_USER") or "postgres",
            "PASSWORD": os.getenv("POSTGRES_PASSWORD") or "",
            "HOST": os.getenv("POSTGRES_HOST") or "localhost",
            "PORT": os.getenv("POSTGRES_PORT") or 5432,
        }
    })


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.authn.password_validation.CommonPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "frontend/static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth

CLUB_BASE_URL = "https://vas3k.club"
CLUB_OPENID_CONFIG = {
    "name": "club",
    "client_id": "vas3k_blog",
    "client_secret": os.getenv("CLUB_OPENID_CONFIG_SECRET") or "vas3k_blog",
    "api_base_url": CLUB_BASE_URL,
    "server_metadata_url": f"{CLUB_BASE_URL}/.well-known/openid-configuration",
    "client_kwargs": {"scope": "openid"},
}

PATREON_AUTH_URL = "https://www.patreon.com/oauth2/authorize"
PATREON_TOKEN_URL = "https://www.patreon.com/api/oauth2/token"
PATREON_USER_URL = "https://www.patreon.com/api/oauth2/v2/identity"
PATREON_CLIENT_ID = os.getenv("PATREON_CLIENT_ID")
PATREON_CLIENT_SECRET = os.getenv("PATREON_CLIENT_SECRET")
PATREON_SCOPE = "identity identity[email]"

# Email

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "email-smtp.eu-central-1.amazonaws.com")
EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "Вастрик <inside@inside.vas3k.ru>"

# Telegram

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_MAIN_CHAT_ID = os.getenv("TELEGRAM_MAIN_CHAT_ID")

# App specific

AUTH_USER_MODEL = "users.User"

SESSION_COOKIE_AGE = 300 * 24 * 60 * 60  # 300 days
SENTRY_DSN = os.getenv("SENTRY_DSN")

APP_HOST = "vas3k.blog"
MIRRORS = ["vas3k.ru"]

CSRF_TRUSTED_ORIGINS = [
    "https://vas3k.blog",
    "https://*.vas3k.blog",
    "https://vas3k.ru",
    "https://*.vas3k.ru",
]

AUTHOR = "@vas3k"
TITLE = "Вастрик"
DESCRIPTION = "Авторский блог о выживании в мире технологий и происходящем вокруг киберпанке"

STYLES_HASH = os.getenv("GITHUB_SHA") or str(randint(1, 10000))

MAX_COMMENTS_PER_24H = 50

if SENTRY_DSN and not DEBUG:
    # activate sentry on production
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[
        DjangoIntegration(),
    ])

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
