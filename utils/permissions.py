from typing import Optional, Tuple, List

from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import APIException

from utils.session import Session


class ArgsPermission(permissions.BasePermission):
    """Base class for permissions that accept arguments."""

    def __call__(self):
        return self


class OrPermission(ArgsPermission):
    """
    Permission that requires any one of multiple permissions.

    Use case: Allow access if user meets any of several permission requirements.
    """

    def __init__(self, *perms) -> None:
        """
        Initialize OR permission.

        Args:
            *perms: Permission classes or instances to check
        """
        self.perms: List = [p() if isinstance(p, type) else p for p in perms]

    def has_permission(self, request, view) -> bool:
        """
        Check if user has at least one of the required permissions.

        Returns:
            True if any permission passes

        Raises:
            APIException: First permission error if all fail
        """
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
    """Exception raised when authentication fails."""

    status_code: int = status.HTTP_401_UNAUTHORIZED
    default_detail: str = "Authentication Error"
    default_code: str = "access_denied"


class AccessError(APIException):
    """Exception raised when user lacks required permissions."""

    status_code: int = status.HTTP_403_FORBIDDEN
    default_detail: str = "Access Denied"
    default_code: str = "access_denied"


class IsAuthenticated(permissions.BasePermission):
    """
    Permission that requires user authentication.

    Use case: Protect endpoints that require valid user login.
    """

    def has_permission(self, request, view) -> bool:
        """Check if user is authenticated."""
        if request.user and request.user.is_authenticated:
            return True
        raise AuthenticationError("Authentication Error!")


class IsAdmin(permissions.BasePermission):
    """
    Permission that requires staff or superuser status.

    Use case: Protect admin-only management endpoints.
    """

    def has_permission(self, request, view) -> bool:
        if (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        ):
            return True
        raise AccessError("Admin access required.")


class TokenAuthentication(BaseAuthentication):
    """
    Authentication via Bearer token in Authorization header.

    Use case: Standard API authentication with session management and auto-refresh.
    """

    def authenticate(self, request) -> Optional[Tuple[User, str]]:
        """
        Authenticate user from Authorization header.

        Process:
        1. Extract Bearer token from Authorization header
        2. Initialize and validate session
        3. Retrieve user from session
        4. Auto-refresh session expiration
        5. Set user and session on request

        Returns:
            Tuple of (user, token) if valid, None if no token

        Raises:
            AuthenticationError: If token or session is invalid
        """
        token: Optional[str] = request.META.get("HTTP_AUTHORIZATION")
        if not (token and token.startswith("Bearer ")):
            return None

        token = token[7:]  # Remove "Bearer " prefix

        # Validate session
        session: Optional[Session] = Session(token=token).initialize()
        if not (session and session.is_accessable):
            raise AuthenticationError("Invalid Token")

        # Authenticate user
        user: Optional[User] = session.get_user()
        if not user:
            raise AuthenticationError("Invalid User Token")
        if not user.is_active:
            raise AuthenticationError("User is not Active")

        request.user = user
        request.session = session

        # Auto-refresh session expiration
        session.refresh()
        return user, session.token
