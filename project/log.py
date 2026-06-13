import ast
import json
import logging
import os
import sys
from datetime import datetime

from tools.datetimes import jdt

PROCESS_TYPE = os.getenv("PROCESS_TYPE", "django")


class JsonFormatter(logging.Formatter):
    """Structured JSON Formatter for ELK"""

    def format(self, record: logging.LogRecord) -> str:

        # Parse message
        try:
            details = ast.literal_eval(record.getMessage())
        except (SyntaxError, ValueError):
            details = record.getMessage()

        # Data
        log_record = {
            "@timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "jalali_datetime": jdt.datetime.fromgregorian(
                datetime=datetime.fromtimestamp(record.created)
            ).isoformat()
            + "Z",
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "file": record.filename,
            "line": record.lineno,
            "process": PROCESS_TYPE,
        }

        if record.exc_info:
            log_record["error_title"] = record.exc_info[0].__name__
            log_record["error_message"] = str(record.exc_info[1])

        if isinstance(details, dict):
            log_record["extra"] = details
            log_record["message"] = None
        else:
            log_record["message"] = details
            log_record["extra"] = None

        return json.dumps(log_record, ensure_ascii=False, default=str)


def logger_set(app: str) -> logging.Logger:
    """Create a logger that supervisor captures into the process log file."""
    logger = logging.getLogger(app)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JsonFormatter())
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(stream_handler)

    return logger
