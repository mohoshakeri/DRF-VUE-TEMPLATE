import os

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from project.settings import (
    ADMIN_PATH,
    APP_BASE_URL,
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
API_PREFIX: str = "api/{}".format(VERSION_CODE)

urlpatterns = [
    # Admin panel endpoints
    path("{}/".format(ADMIN_PATH), include("massadmin.urls")),
    # API endpoints
    path("{}/auth/".format(API_PREFIX), include("authentication.urls")),
]

# Admin panel customization
admin.AdminSite.site_title = "project"
admin.AdminSite.site_header = "project"
admin.AdminSite.site_url = APP_BASE_URL
admin.AdminSite.empty_value_display = "* * *"


if not IS_PRODUCTION:
    urlpatterns += static(STATIC_URL, document_root=os.path.join(BASE_DIR, "static"))
    urlpatterns += static(ASSETS_URL, document_root=os.path.join(BASE_DIR, "assets"))
