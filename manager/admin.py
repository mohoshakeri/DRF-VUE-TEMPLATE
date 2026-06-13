from django.contrib import admin

from utils.admin import AbstractAdmin
from .models import *


@admin.register(CronJobExecution)
class CronJobExecutionAdmin(AbstractAdmin):
    search_fields = ("name", "error", "output")
    display_excludes = (
        "pk",
        "args",
        "kwargs",
        "result",
        "output",
        "traceback",
    )
    list_filter = ("job_type", "status", "is_successful", "name")
