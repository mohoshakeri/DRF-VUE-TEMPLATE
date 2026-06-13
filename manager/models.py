from typing import Optional, Dict, List, Any

from django.db import models

from CONSTANTS import (
    CRON_JOB_STATUSES,
    CRON_JOB_STATUS_FAILED,
    CRON_JOB_STATUS_RUNNING,
    CRON_JOB_STATUS_SUCCESS,
    CRON_JOB_TYPE_CELERY,
    CRON_JOB_TYPES,
)
from tools.datetimes import dt
from utils.db import AbstractModel


class CronJobExecution(AbstractModel):
    """
    Cron job execution tracking.

    Use case: Track scheduled management commands and celery tasks that are
    executed from system crontab.
    """

    job_type: int = models.IntegerField(
        choices=CRON_JOB_TYPES,
        default=CRON_JOB_TYPE_CELERY,
    )
    name: str = models.CharField(max_length=200)
    status: int = models.IntegerField(
        choices=CRON_JOB_STATUSES,
        default=CRON_JOB_STATUS_RUNNING,
    )
    is_successful: bool = models.BooleanField(default=False)
    started_at: dt.datetime = models.DateTimeField(default=dt.datetime.now)
    finished_at: Optional[dt.datetime] = models.DateTimeField(null=True, blank=True)
    duration_seconds: Optional[float] = models.FloatField(null=True, blank=True)
    args: List[Any] = models.JSONField(default=list, blank=True)
    kwargs: Dict[str, Any] = models.JSONField(default=dict, blank=True)
    result: Optional[Any] = models.JSONField(null=True, blank=True)
    output: Optional[str] = models.TextField(null=True, blank=True)
    error: Optional[str] = models.TextField(null=True, blank=True)
    traceback: Optional[str] = models.TextField(null=True, blank=True)
    executed_by: str = models.CharField(max_length=50, default="crontab")

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["job_type", "name", "-started_at"]),
            models.Index(fields=["status", "-started_at"]),
        ]

    def __str__(self):
        return "{} - {} - {}".format(self.name, self.status, self.started_at)

    def finish_success(self, result: Any = None, output: str = "") -> None:
        self.status = CRON_JOB_STATUS_SUCCESS
        self.is_successful = True
        self.result = result
        self.output = output
        self._finish()

    def finish_failed(self, error: str, traceback: str = "", output: str = "") -> None:
        self.status = CRON_JOB_STATUS_FAILED
        self.is_successful = False
        self.error = error
        self.traceback = traceback
        self.output = output
        self._finish()

    def _finish(self) -> None:
        self.finished_at = dt.datetime.now()
        self.duration_seconds = (self.finished_at - self.started_at).total_seconds()
        self.save()
