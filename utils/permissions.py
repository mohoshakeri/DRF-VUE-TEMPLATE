from typing import Any, List, Optional, Tuple

from rest_framework import permissions, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import APIException

from utils.session import Session


class ArgsPermission(permissions.BasePermission):
    def __call__(self) -> "ArgsPermission":
        return self


class OrPermission(ArgsPermission):
    def __init__(self, *perms: Any) -> None:
        self.perms: List = [p() if isinstance(p, type) else p for p in perms]

    def has_permission(self, request: Any, view: Any) -> bool:
        errors: List[APIException] = []
        for perm in self.perms:
            try:
                if perm.has_permission(request, view):
                    return True
            except APIException as exc:
                errors.append(exc)

        if errors:
            raise errors[0]
        return False


class AuthenticationError(APIException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    default_detail: str = "Authentication Error"
    default_code: str = "access_denied"


class AccessError(APIException):
    status_code: int = status.HTTP_403_FORBIDDEN
    default_detail: str = "Access Denied"
    default_code: str = "access_denied"


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request: Any, view: Any) -> bool:
        if request.user and request.user.is_authenticated:
            return True
        raise AuthenticationError("Authentication Error!")


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request: Any, view: Any) -> bool:
        if (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        ):
            return True
        raise AccessError("Admin access required.")


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request: Any) -> Optional[Tuple[Any, str]]:
        token: Optional[str] = request.META.get("HTTP_AUTHORIZATION")
        if not (token and token.startswith("Bearer ")):
            return None

        token = token[7:]

        session: Optional[Session] = Session(token=token).initialize()
        if not (session and session.is_accessable):
            raise AuthenticationError("Invalid Token")

        user: Optional[Any] = session.get_user()
        if not user:
            raise AuthenticationError("Invalid User Token")
        if not user.is_active:
            raise AuthenticationError("User is not Active")

        request.user = user
        request.auth_session = session

        session.refresh()
        return user, session.token
