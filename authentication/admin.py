from django.contrib import admin
from django.contrib.auth.models import Group
from django_celery_results.models import GroupResult

from utils.admin import AbstractAdmin
from .models import *

admin.site.unregister(Group)
admin.site.unregister(GroupResult)


@admin.register(User)
class UserAdmin(AbstractAdmin):
    search_fields = ("mobile", "name")
    display_excludes = (
        "password",
        "groups",
        "user_permissions",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
