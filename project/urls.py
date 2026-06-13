import os

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, register_converter

from project.settings import (
    ADMIN_PATH,
    CORE_BASE_URL,
    STATIC_URL,
    IS_PRODUCTION,
    BASE_DIR,
    ASSETS_URL,
)
from utils.converters import DatetimeConverter, BoolConverter, DateConverter

# Register custom URL path converters
register_converter(BoolConverter, "bool")
register_converter(DatetimeConverter, "datetime")
register_converter(DateConverter, "date")

# API configuration
VERSION_CODE: str = "v1"
API_PREFIX: str = f"api/{VERSION_CODE}"

urlpatterns = [
    # Admin panel endpoints
    path(f"{ADMIN_PATH}/", include("massadmin.urls")),
    # API endpoints
    path(f"{API_PREFIX}/auth/", include("example.urls")),
]

# Admin panel customization
admin.AdminSite.site_title = "project"
admin.AdminSite.site_header = "project"
admin.AdminSite.site_url = CORE_BASE_URL
admin.AdminSite.empty_value_display = "* * *"


if not IS_PRODUCTION:
    urlpatterns += static(STATIC_URL, document_root=os.path.join(BASE_DIR, "static"))
    urlpatterns += static(ASSETS_URL, document_root=os.path.join(BASE_DIR, "assets"))
