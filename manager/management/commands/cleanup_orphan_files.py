import os
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = "Delete files under MEDIA_ROOT upload directories that are not referenced by FileField values."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only report orphan files without deleting them.",
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT).resolve()
        referenced_files, managed_dirs = self._collect_filefield_state(media_root)
        managed_dirs = self._collapse_dirs(managed_dirs)

        orphan_files = []
        for managed_dir in sorted(managed_dirs):
            absolute_dir = media_root / managed_dir
            if not absolute_dir.is_dir():
                continue
            for path in absolute_dir.rglob("*"):
                if not path.is_file():
                    continue
                relative_path = self._relative_media_path(path, media_root)
                if relative_path and relative_path not in referenced_files:
                    orphan_files.append(path)

        if options["dry_run"]:
            action = "Found"
        else:
            action = "Deleted"
            for path in orphan_files:
                path.unlink()

        self.stdout.write(
            self.style.SUCCESS(
                "{} {} orphan file(s) in {} managed directorie(s).".format(
                    action,
                    len(orphan_files),
                    len(managed_dirs),
                )
            )
        )
        if options["verbosity"] >= 2:
            for path in orphan_files:
                self.stdout.write(str(path.relative_to(media_root)))

    def _collect_filefield_state(self, media_root: Path):
        referenced_files = set()
        managed_dirs = set()

        for model in apps.get_models():
            file_fields = [
                field
                for field in model._meta.fields
                if isinstance(field, models.FileField)
            ]
            if not file_fields:
                continue

            for field in file_fields:
                upload_dir = self._upload_dir_for_field(model, field)
                if upload_dir:
                    managed_dirs.add(upload_dir)

                values = (
                    model._default_manager.exclude(
                        **{"{}__isnull".format(field.name): True}
                    )
                    .exclude(**{field.name: ""})
                    .values_list(field.name, flat=True)
                    .iterator()
                )
                for value in values:
                    relative_path = self._normalize_relative_path(value)
                    if not relative_path:
                        continue
                    absolute_path = (media_root / relative_path).resolve()
                    if not self._is_inside_media_root(absolute_path, media_root):
                        continue
                    referenced_files.add(relative_path)
                    managed_dirs.add(os.path.dirname(relative_path))

        return referenced_files, {path for path in managed_dirs if path}

    def _upload_dir_for_field(self, model, field):
        upload_to = field.upload_to
        if isinstance(upload_to, str):
            return self._normalize_relative_path(upload_to)

        try:
            instance = model()
            generated_name = field.generate_filename(
                instance,
                "__cleanup_probe__.bin",
            )
        except Exception:
            return ""

        generated_name = self._normalize_relative_path(generated_name)
        return os.path.dirname(generated_name) if generated_name else ""

    def _normalize_relative_path(self, value):
        if not value:
            return ""
        normalized = os.path.normpath(str(value).replace("\\", "/")).replace("\\", "/")
        normalized = normalized.lstrip("/")
        if normalized in {"", "."} or normalized.startswith("../"):
            return ""
        return normalized

    def _relative_media_path(self, path: Path, media_root: Path):
        resolved_path = path.resolve()
        if not self._is_inside_media_root(resolved_path, media_root):
            return ""
        return resolved_path.relative_to(media_root).as_posix()

    def _is_inside_media_root(self, path: Path, media_root: Path):
        return path == media_root or media_root in path.parents

    def _collapse_dirs(self, dirs):
        collapsed = []
        for directory in sorted(dirs):
            if any(
                directory == parent or directory.startswith("{}/".format(parent))
                for parent in collapsed
            ):
                continue
            collapsed.append(directory)
        return collapsed
