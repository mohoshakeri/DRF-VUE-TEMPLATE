from .base import *

IS_PRODUCTION = False
DEBUG = False
SECRET_KEY = "ktvI9-rYqmgR8aDNVYqAnZ5ErWAVTj552OIouLEqyzg="
REDIS_SERVER = "redis://localhost:6379/15"
ADMIN_PATH = "admin"
APP_BASE_URL = "http://testserver"
CORE_BASE_URL = "{}{}".format(APP_BASE_URL, CORE_BASE_PATH)
FORCE_SCRIPT_NAME = CORE_BASE_PATH
ALLOWED_HOSTS = ["testserver", "localhost"]
ORIGINS = [APP_BASE_URL]
LOG_DIR = os.path.join(BASE_DIR, "logs")
CELERY_BROKER_URL = REDIS_SERVER
MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE
    if middleware != "author.middlewares.AuthorDefaultBackendMiddleware"
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "project-tests",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
