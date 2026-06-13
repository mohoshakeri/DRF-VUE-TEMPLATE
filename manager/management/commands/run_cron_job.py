import json
import traceback as traceback_module
from io import StringIO
from typing import Any, Dict, List

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from CONSTANTS import CRON_JOB_TYPE_CELERY, CRON_JOB_TYPE_COMMAND
from manager.models import CronJobExecution
from services.celery import app as celery_app


class Command(BaseCommand):
    help = "Run a tracked cron job as a management command or celery task."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "job_type",
            choices=("celery", "command"),
            help="Cron job type.",
        )
        parser.add_argument(
            "name",
            help="Celery task name or Django management command name.",
        )
        parser.add_argument(
            "--task-args",
            dest="task_args",
            default="[]",
            help="JSON list of positional arguments.",
        )
        parser.add_argument(
            "--task-kwargs",
            dest="task_kwargs",
            default="{}",
            help="JSON object of keyword arguments.",
        )
        parser.add_argument(
            "--executed-by",
            default="crontab",
            help="Execution source label.",
        )

    def handle(self, *args, **options) -> None:
        job_type: str = options["job_type"]
        name: str = options["name"]
        parsed_args: List[Any] = self._parse_json_list(options["task_args"])
        parsed_kwargs: Dict[str, Any] = self._parse_json_dict(options["task_kwargs"])
        execution_type: int = (
            CRON_JOB_TYPE_CELERY if job_type == "celery" else CRON_JOB_TYPE_COMMAND
        )
        execution: CronJobExecution = CronJobExecution.objects.create(
            job_type=execution_type,
            name=name,
            args=parsed_args,
            kwargs=parsed_kwargs,
            executed_by=options["executed_by"],
        )

        try:
            result: Any
            output: str = ""
            if job_type == "celery":
                result = self._run_celery_task(name, parsed_args, parsed_kwargs)
            else:
                result, output = self._run_management_command(
                    name,
                    parsed_args,
                    parsed_kwargs,
                )

            execution.finish_success(
                result=self._json_safe(result),
                output=output,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Cron job {} finished successfully.".format(execution.id)
                )
            )
        except Exception as exc:
            trace: str = traceback_module.format_exc()
            execution.finish_failed(
                error=str(exc),
                traceback=trace,
            )
            raise CommandError(
                "Cron job {} failed: {}".format(execution.id, exc)
            ) from exc

    def _run_celery_task(
        self,
        name: str,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> Any:
        task = celery_app.tasks.get(name)
        if not task:
            celery_app.loader.import_default_modules()
            task = celery_app.tasks.get(name)

        if not task:
            raise CommandError("Celery task not found: {}".format(name))

        result = task.apply(args=args, kwargs=kwargs, throw=False)
        self._save_celery_task_result(
            name=name,
            args=args,
            kwargs=kwargs,
            result=result,
        )

        if not result.successful():
            if isinstance(result.result, Exception):
                raise result.result
            raise CommandError(str(result.result))

        return result.result

    def _save_celery_task_result(
        self,
        name: str,
        args: List[Any],
        kwargs: Dict[str, Any],
        result: Any,
    ) -> None:
        from django_celery_results.models import TaskResult
        from tools.datetimes import dt

        task_result = TaskResult.objects.get_or_create(
            task_id=result.id,
            defaults={
                "task_name": name,
                "task_args": json.dumps(args, default=str),
                "task_kwargs": json.dumps(kwargs, default=str),
                "content_type": "application/json",
                "content_encoding": "utf-8",
            },
        )[0]
        task_result.task_name = name
        task_result.task_args = json.dumps(args, default=str)
        task_result.task_kwargs = json.dumps(kwargs, default=str)
        task_result.status = result.status
        task_result.result = json.dumps(
            self._json_safe(result.result),
            ensure_ascii=False,
        )
        task_result.traceback = result.traceback or ""
        task_result.content_type = "application/json"
        task_result.content_encoding = "utf-8"
        task_result.date_done = dt.datetime.now()
        task_result.save()

    def _run_management_command(
        self,
        name: str,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> tuple[Any, str]:
        stdout: StringIO = StringIO()
        stderr: StringIO = StringIO()
        result: Any = call_command(
            name,
            *args,
            stdout=stdout,
            stderr=stderr,
            **kwargs,
        )
        output: str = "{}{}".format(stdout.getvalue(), stderr.getvalue())
        return result, output

    def _parse_json_list(self, value: str) -> List[Any]:
        parsed: Any = json.loads(value)
        if not isinstance(parsed, list):
            raise CommandError("--task-args must be a JSON list.")
        return parsed

    def _parse_json_dict(self, value: str) -> Dict[str, Any]:
        parsed: Any = json.loads(value)
        if not isinstance(parsed, dict):
            raise CommandError("--task-kwargs must be a JSON object.")
        return parsed

    def _json_safe(self, value: Any) -> Any:
        return json.loads(json.dumps(value, default=str))
