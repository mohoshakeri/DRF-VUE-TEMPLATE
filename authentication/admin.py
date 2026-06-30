from django.contrib import admin
from django.contrib.auth.models import Group
from django_celery_results.models import GroupResult

from utils.admin import AbstractAdmin
from .models import *

admin.site.unregister(Group)
admin.site.unregister(GroupResult)


@admin.register(User)
class UserAdmin(AbstractAdmin):
    list_display = ("id", "mobile", "name", "is_active", "is_staff", "create")
    search_fields = ("mobile", "name")
    list_filter = ("is_active", "is_staff", "is_superuser")
