from datetime import datetime

from django.db import models, transaction, IntegrityError
from django.db.models import Q, F

from tools.converters import md_to_html

db_transaction = transaction

__all__ = [
    "AbstractModel",
    "MarkdownField",
    "models",
    "db_transaction",
    "IntegrityError",
    "Q",
    "F",
]


class AbstractModel(models.Model):
    """
    Abstract base model with timestamps and hashed ID.

    Use case: Provide automatic timestamps and obfuscated ID encoding for all models.
    """

    id: int = models.AutoField(primary_key=True)
    create: datetime = models.DateTimeField(auto_now_add=True)
    update: datetime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MarkdownText(str):
    def as_html(self):
        return md_to_html(self)


class MarkdownField(models.TextField):
    """
    Markdown text field.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize encrypted text field."""
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if isinstance(value, MarkdownText):
            return str(value)
        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return MarkdownText(value)
