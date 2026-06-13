from .base import *

IS_PRODUCTION = False
DEBUG = False
SECRET_KEY = "ktvI9-rYqmgR8aDNVYqAnZ5ErWAVTj552OIouLEqyzg="
REDIS_SERVER = "redis://localhost:6379/15"
ADMIN_PATH = "admin"
CORE_DOMAIN = "testserver"
CORE_BASE_URL = "http://{}".format(CORE_DOMAIN)
APP_DOMAIN = "testclient"
APP_BASE_URL = "http://{}".format(APP_DOMAIN)
ALLOWED_HOSTS = ["testserver", "localhost"]
ORIGINS = ["http://testclient"]
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
