"""
Template tags
"""

from django import template
from django.urls import reverse

from project.settings import CORE_BASE_URL, STATIC_URL, ASSETS_URL, MEDIA_URL
from tools.converters import md_to_html, number_to_string, add_thousand_separator
from tools.datetimes import dt_to_text

register = template.Library()
DEFAULT = "***"


@register.filter
def add(int1, int2):
    return int1 + int2


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item_or_zero(dictionary, key) -> int:
    item = dictionary.get(key)
    if item is not None:
        return item
    return 0


@register.filter
def get_index(list, index):
    return list[index - 1]


@register.filter
def standard_datetime(datetime, default=DEFAULT):
    if datetime:
        return dt_to_text(datetime)
    return default


@register.filter
def standard_date(datetime, default=DEFAULT):
    if datetime:
        return dt_to_text(datetime, time_check=False)
    return default


@register.filter
def datetime_diff(datetime2, datetime1):
    return (datetime2 - datetime1).days // 365


@register.filter
def en_datetime(datetime, default=DEFAULT):
    if datetime:
        return dt_to_text(datetime, lang="English")
    return default


@register.filter
def md_to_html(content, default=DEFAULT):
    if content:
        return md_to_html(content)
    return default


@register.filter
def to_string(content, default=DEFAULT):
    if content:
        return number_to_string(content)
    return default


@register.filter
def to_iso_number(number, default=DEFAULT):
    if number:
        return add_thousand_separator(number)
    if number == 0:
        return 0
    return default


@register.filter
def multiply(number1, number2):
    return number1 * number2


@register.simple_tag
def disk(path: str):
    if path.startswith(("img", "audio", "video")):
        return f"{CORE_BASE_URL}{ASSETS_URL}{path}"
    if path.startswith("storage"):
        return f"{CORE_BASE_URL}{MEDIA_URL}{path.replace('storage', '')}"
    return f"{CORE_BASE_URL}{STATIC_URL}{path}"


def _site_disk_path(path: str) -> str:
    if path.startswith(("img", "audio", "video")):
        return f"{ASSETS_URL}{path}"
    if path.startswith("storage"):
        return f"{MEDIA_URL}{path.replace('storage', '')}"
    return f"{STATIC_URL}{path}"


@register.simple_tag(takes_context=True)
def site_disk(context, path: str):
    path = _site_disk_path(path)
    site = context.get("site")
    if context.get("seo") and site:
        return f"https://{site.domain}{path}"
    return path


@register.simple_tag(takes_context=True)
def site_url(context, route: str, blog_id=None):
    site = context.get("site")
    if not site:
        return "#"

    if context.get("is_proxy_request"):
        if route == "home":
            return "/"
        if route == "blog":
            return f"/blog/{blog_id}/"
        if route == "sitemap":
            return "/sitemap.xml"
        if route == "favicon":
            return "/favicon.ico"
        if route == "analysis_collect":
            return "/analytics/collect/"
        return "/"

    if route == "home":
        return reverse("website:render", kwargs={"domain": site.domain})
    if route == "blog":
        return reverse(
            "website:render_blog",
            kwargs={"domain": site.domain, "blog_id": blog_id},
        )
    if route == "sitemap":
        return reverse("website:render_sitemap", kwargs={"domain": site.domain})
    if route == "favicon":
        return reverse("website:render_favicon", kwargs={"domain": site.domain})
    if route == "analysis_collect":
        return reverse("website:analysis_collect", kwargs={"domain": site.domain})
    return reverse("website:render", kwargs={"domain": site.domain})


@register.filter
def fix_enters(text):
    return text.replace("\n", "<br>")
