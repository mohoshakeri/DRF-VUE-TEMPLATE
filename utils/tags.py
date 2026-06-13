from datetime import date, datetime
from typing import Any

from django import template
from django.template.defaultfilters import linebreaksbr

from project.settings import APP_BASE_URL, ASSETS_URL, MEDIA_URL, STATIC_URL
from tools.converters import (
    add_thousand_separator,
    md_to_html as markdown_to_html,
    number_to_string,
    persian_english_converter,
)
from tools.datetimes import dt_to_text

register = template.Library()
DEFAULT: str = "***"


# --- Collection Filters ---


@register.filter(name="add")
def add_values(first: Any, second: Any) -> Any:
    try:
        return first + second
    except TypeError:
        return first


@register.filter
def get_item(dictionary: dict | None, key: Any) -> Any:
    if not dictionary:
        return None
    return dictionary.get(key)


@register.filter
def get_item_or_zero(dictionary: dict | None, key: Any) -> Any:
    item: Any = get_item(dictionary, key)
    if item is not None:
        return item
    return 0


@register.filter
def get_index(items: list | tuple, index: int) -> Any:
    try:
        return items[int(index) - 1]
    except (IndexError, TypeError, ValueError):
        return DEFAULT


# --- Date Filters ---


@register.filter
def standard_datetime(value: datetime | date | None, default: str = DEFAULT) -> str:
    if value:
        return dt_to_text(value)
    return default


@register.filter
def standard_date(value: datetime | date | None, default: str = DEFAULT) -> str:
    if value:
        return dt_to_text(value, time_check=False)
    return default


@register.filter
def en_datetime(value: datetime | date | None, default: str = DEFAULT) -> str:
    if value:
        return dt_to_text(value, lang="English")
    return default


@register.filter
def datetime_diff(start: datetime | date, end: datetime | date) -> int:
    return (start - end).days // 365


# --- Text And Number Filters ---


@register.filter(name="md_to_html")
def render_markdown(content: Any, default: str = DEFAULT) -> str:
    if content:
        return markdown_to_html(str(content))
    return default


@register.filter
def to_string(content: Any, default: str = DEFAULT) -> str:
    if content is not None and content != "":
        return number_to_string(content)
    return default


@register.filter
def to_iso_number(number: Any, default: str = DEFAULT) -> str | int:
    if number:
        return add_thousand_separator(number)
    if number == 0:
        return 0
    return default


@register.filter
def english_digits(content: Any) -> str:
    return persian_english_converter(str(content))


@register.filter
def persian_digits(content: Any) -> str:
    return persian_english_converter(str(content), reverse=True)


@register.filter
def fix_enters(text: Any) -> str:
    if text is None:
        return ""
    return linebreaksbr(str(text))


# --- Math Filters ---


@register.filter
def multiply(number1: int | float, number2: int | float) -> int | float:
    return number1 * number2


@register.filter
def divide(number1: int | float, number2: int | float) -> float | None:
    if not number2:
        return None
    return number1 / number2


@register.filter
def percent(number: int | float, total: int | float) -> float:
    if not total:
        return 0
    return round((number / total) * 100, 2)


# --- URL Tags ---


def _asset_path(path: str) -> str:
    clean_path: str = str(path).lstrip("/")
    if clean_path.startswith(("http://", "https://")):
        return clean_path
    if clean_path.startswith(("img", "audio", "video")):
        return "{}{}".format(ASSETS_URL, clean_path)
    if clean_path == "storage":
        return MEDIA_URL
    if clean_path.startswith("storage/"):
        return "{}{}".format(MEDIA_URL, clean_path[len("storage/") :])
    return "{}{}".format(STATIC_URL, clean_path)


@register.simple_tag
def disk(path: str) -> str:
    asset_path: str = _asset_path(path)
    if asset_path.startswith(("http://", "https://")):
        return asset_path
    return "{}{}".format(APP_BASE_URL.rstrip("/"), asset_path)


@register.simple_tag(takes_context=True)
def site_disk(context: dict, path: str) -> str:
    asset_path: str = _asset_path(path)
    site: Any = context.get("site")
    if context.get("seo") and site:
        return "https://{}{}".format(site.domain, asset_path)
    return asset_path


@register.simple_tag(takes_context=True)
def query_update(context: dict, **kwargs: Any) -> str:
    request: Any = context.get("request")
    if not request:
        return ""

    query = request.GET.copy()
    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
            continue
        query[key] = value

    return query.urlencode()
