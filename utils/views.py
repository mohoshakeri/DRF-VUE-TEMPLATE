from typing import Any

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView


class HTTPError(Exception):
    def __init__(
        self,
        message: str | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: dict[str, Any] | None = None,
    ) -> None:
        if data is None:
            data = {}

        if message:
            data["message"] = message
        self.status_code = status_code
        self.data = data


def get_object_or_error(
    status_code: int,
    message: str | None,
    queryset: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    target = (
        queryset._default_manager.all()
        if hasattr(queryset, "_default_manager")
        else queryset
    )

    if message is None:
        message = "Object not found [404]"

    if not hasattr(target, "get"):
        klass_name = (
            queryset.__name__
            if isinstance(queryset, type)
            else queryset.__class__.__name__
        )
        raise ValueError(
            "First argument to get_object_or_error() must be a Model, Manager, "
            "or QuerySet, not '{}'.".format(klass_name)
        )

    try:
        return target.get(*args, **kwargs)
    except target.model.DoesNotExist as exc:
        raise HTTPError(message=message, status_code=status_code) from exc


class BaseView(APIView):
    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            response = super().dispatch(request, *args, **kwargs)
            return response
        except HTTPError as exc:
            return JsonResponse(data=exc.data, status=exc.status_code)
