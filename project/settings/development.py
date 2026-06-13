import sys

from .base import *

# Development status
IS_PRODUCTION = False
DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "xxx",
        "USER": "postgres",
        "PASSWORD": "1234",
        "HOST": "localhost",
        "PORT": "5432",
        "CONN_MAX_AGE": 0,  # Control by pooler
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "pool": {
                "min_size": 5,
                "max_size": 15,
                "max_lifetime": 24 * 60 * 60,
            }
        },
    }
}

# Redis configuration
REDIS_SERVER = "redis://localhost:6379/0"

# Cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_SERVER,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        },
    }
}

# Security keys
KEY = "ktvI9-rYqmgR8aDNVYqAnZ5ErWAVTj552OIouLEqyzg="
SECRET_KEY = KEY


# Path and URLs
CORE_BASE_PATH = "/"
ADMIN_PATH = "admin"
APP_BASE_URL = "http://localhost:4130"
CORE_BASE_URL = "{}{}".format(APP_BASE_URL, CORE_BASE_PATH)
FORCE_SCRIPT_NAME = CORE_BASE_PATH

# Hosts and origins
HOSTS = ["localhost"]
ALLOWED_HOSTS = ["*"]
ORIGINS = [APP_BASE_URL]

# Security configuration
IP_BLOCKEDS = []
SECURITY_MOBILE = "0910XXXXXXX"

# Static files configuration (development)
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = None

# Logging configuration
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Celery broker
CELERY_BROKER_URL = REDIS_SERVER

# CORS configuration
if len(sys.argv) > 1 and sys.argv[1] not in MANAGEMENT_ARGS:
    CORS_ALLOWED_ORIGINS = ORIGINS
    CORS_ALLOW_METHODS = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ]
