"""
Date and time utilities for Persian (Jalali) and Gregorian calendars.

This module provides functions for formatting dates and times in both
Persian and English, with support for Jalali calendar conversion.
"""

import datetime

import jdatetime

from CONSTANTS import ENGLISH_MONTHS, PERSIAN_MONTHS

dt = datetime
jdt = jdatetime


def format_time(hour: int, minute: int) -> str:
    """
    Format time as HH:MM string.

    Args:
        hour: Hour value (0-23)
        minute: Minute value (0-59)

    Returns:
        Formatted time string in HH:MM format
    """
    return "{:02}:{:02}".format(hour, minute)


def format_date_text(
    day: str,
    month: str,
    year: str = "",
    time_text: str = "",
    lang: str = "Persian",
) -> str:
    """
    Format date components into a readable text string.

    Use case: Generate human-readable date strings for display in UI or reports.

    Args:
        day: Day of month
        month: Month name
        year: Year (optional)
        time_text: Time string (optional)
        lang: Language for formatting ("Persian" or "English")

    Returns:
        Formatted date text string
    """
    if lang == "Persian":
        date_text: str = "{} {}".format(day, month) + (
            " {}".format(year) if year else ""
        )
        return date_text + (" - ساعت {}".format(time_text) if time_text else "")
    else:
        date_text: str = "{} {}".format(month, day) + (
            ", {}".format(year) if year else ""
        )
        return date_text + (" at {}".format(time_text) if time_text else "")


def dt_to_text(
    datetime_obj: datetime.datetime,
    time_check: bool = True,
    year_check: bool = True,
    lang: str = "Persian",
) -> str:
    """
    Convert datetime object to human-readable text.

    Use case: Display dates in user-friendly format for both Persian and English locales.

    Process:
    1. Handle None and date-only objects
    2. Convert to Jalali calendar for Persian, use Gregorian for English
    3. Extract date components and format as text
    4. Include time and year based on parameters

    Args:
        datetime_obj: Datetime object to convert
        time_check: Include time in output
        year_check: Include year in output
        lang: Language for output ("Persian" or "English")

    Returns:
        Formatted date text string, empty string if input is None
    """
    if not datetime_obj:
        return ""

    # Convert date to datetime if necessary
    if isinstance(datetime_obj, dt.date) and not isinstance(datetime_obj, dt.datetime):
        datetime_obj = dt.datetime.combine(datetime_obj, dt.datetime.min.time())

    if lang == "Persian":
        jalali: jdt.datetime = jdt.datetime.fromgregorian(datetime=datetime_obj)
        day: str = str(jalali.day)
        month: str = PERSIAN_MONTHS[jalali.month]
        year: str = str(jalali.year)
        hour: int = jalali.hour
        minute: int = jalali.minute
    else:
        day: str = str(datetime_obj.day)
        month: str = ENGLISH_MONTHS[datetime_obj.month]
        year: str = str(datetime_obj.year)
        hour: int = datetime_obj.hour
        minute: int = datetime_obj.minute

    time_text: str = format_time(hour, minute) if time_check else ""
    year_text: str = year if year_check else ""

    return format_date_text(day, month, year_text, time_text, lang)
