from django.contrib import admin

from utils.admin import AbstractAdmin

from .models import *


@admin.register(User)
class UserAdmin(AbstractAdmin):
    search_fields = ("mobile", "name")
    display_excludes = (
        "password",
        "groups",
        "user_permissions",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
