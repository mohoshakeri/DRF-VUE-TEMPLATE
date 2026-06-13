import os
from pathlib import Path
from typing import Dict

from CONSTANTS import (
    ADMIN_SESSION_COOKIE_AGE,
    PAGINATE_PAGE_SIZE,
    VERIFICATION_CODE_THROTTLE_RATES_PER_HOUR,
    ANONYMOUS_THROTTLE_RATES_PER_HOUR,
    USER_THROTTLE_RATES_PER_HOUR,
)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    "django_simorgh",
    "django.contrib.admin",
    "django.contrib.humanize",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_results",
    "django_json_widget",
    "jalali_date_new",
    "corsheaders",
    "massadmin",
    "manager",
    "authentication",
]
AUTH_USER_MODEL = "authentication.User"

# URLs and deployment configuration
ROOT_URLCONF = "project.urls"
WSGI_APPLICATION = "project.wsgi.application"
SHORT_LINK_PATH = "s"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_simorgh.context_processors.simorgh_context",
            ],
            "libraries": {
                "tags": "utils.tags",
            },
        },
    },
]

# Static files configuration
ASSETS_URL = "/assets/"  # By Nginx (IMG - AUDIO - VIDEO)
STATIC_URL = "/static/"  # By Nginx (CSS, JS, FONTS, CDN, APK)
MEDIA_URL = "/storage/"  # By Middleware (Uploads)
MEDIA_ROOT = os.path.join(BASE_DIR, "storage")
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1000 * 10  # 10 MB

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Localization and timezone configuration
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = False

# Management commands that don't need CORS configuration
MANAGEMENT_ARGS = [
    "migrate",
    "loaddata",
    "redisflush",
]

# Password hashing configuration
PASSWORD_HASHERS = [
    "django.contrib.authentication.hashers.BCryptPasswordHasher",
    "django.contrib.authentication.hashers.PBKDF2PasswordHasher",
    "django.contrib.authentication.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.authentication.hashers.Argon2PasswordHasher",
    "django.contrib.authentication.hashers.ScryptPasswordHasher",
]

# Middleware configuration
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "author.middlewares.AuthorDefaultBackendMiddleware",
    "utils.middlewares.IPIdentificationMiddleware",
    "utils.middlewares.IPBlockMiddleware",
    "utils.middlewares.LoggingMiddleware",
    "utils.middlewares.MediaMiddleware",
]

# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_COOKIE_AGE = ADMIN_SESSION_COOKIE_AGE
SESSION_SAVE_EVERY_REQUEST = True

# REST framework configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "utils.permissions.TokenAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": f"{ANONYMOUS_THROTTLE_RATES_PER_HOUR}/hour",
        "user": f"{USER_THROTTLE_RATES_PER_HOUR}/hour",
        "vcode": f"{VERIFICATION_CODE_THROTTLE_RATES_PER_HOUR}/hour",
    },
    "PAGE_SIZE": PAGINATE_PAGE_SIZE,
}

# Mass edit configuration
MASSEDIT = {
    "ADD_ACTION_GLOBALLY": False,
}

# Celery configuration
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tehran"
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND = "django-db"

# Client application redirect URLs
APP_URLS: Dict[str, str] = {}

# Django Simorgh
DJANGO_ADMIN_THEME_COLOR = "blue"
DJANGO_ADMIN_SITE_HEADER = "project"
DJANGO_ADMIN_LOGO = "/assets/img/logo.png"
DJANGO_ADMIN_FAVICON = "/favicon.ico"
