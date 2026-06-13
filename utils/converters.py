import json
import uuid
from datetime import datetime


class DatetimeConverter:
    regex = r"\d{4}-\d{2}-\d{2}--\d{2}:\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d--%H:%M")

    def to_url(self, value):
        return value.strftime("%Y-%m-%d--%H:%M")


class BoolConverter:
    regex = r"0|1"

    def to_python(self, value):
        return value == "1"

    def to_url(self, value):
        return "1" if value else "0"


class DateConverter:
    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d").date()

    def to_url(self, value):
        return value.strftime("%Y-%m-%d")


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)
