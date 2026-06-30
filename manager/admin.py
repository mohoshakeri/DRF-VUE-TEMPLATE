from django.contrib import admin

from utils.admin import AbstractAdmin
from .models import *


@admin.register(CronJobExecution)
class CronJobExecutionAdmin(AbstractAdmin):
    list_display = (
        "id",
        "name",
        "job_type",
        "status",
        "is_successful",
        "started_at",
        "finished_at",
    )
    search_fields = ("name", "error", "output")
    list_filter = ("job_type", "status", "is_successful", "name")
