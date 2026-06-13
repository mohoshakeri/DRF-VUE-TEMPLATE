import secrets
from typing import Optional, Generator

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from pydantic import BaseModel, Field, PrivateAttr

from CONSTANTS import (
    USER_SESSION_KEY_PREFIX,
    USER_SESSION_FULL_AGE,
    USER_SESSION_RENEWAL_AGE,
)
from services.redis import redis_client
from tools.datetimes import dt

SESSION_FULL_AGE: int = USER_SESSION_FULL_AGE
SESSION_RENEWAL_AGE: int = USER_SESSION_RENEWAL_AGE


class ConflictTokenError(Exception):
    """Exception raised when session token already exists."""

    pass


class Session(BaseModel):
    """
    User session with Redis storage and token-based access.

    Use case: Manage user authentication sessions with automatic expiration,
    content storage, and refresh mechanism.

    Usage patterns:
    - GET SESSION: Session(token).initialize() -> get_user() -> use session methods
    - CREATE SESSION: Session(user_id=id).create()

    Notes:
    - is_accessable and get_user only need to be called once in TokenAuthentication
    - Redis stores session data without exact expiration time (checked in session body)
    """

    token: str = Field(default_factory=lambda: secrets.token_urlsafe(64))
    user_id: Optional[int] = Field(default=None)
    content: dict = Field(default_factory=dict)
    expired: float = Field(
        default_factory=lambda: (
            dt.datetime.now() + dt.timedelta(seconds=SESSION_FULL_AGE)
        ).timestamp()
    )
    _user_obj: Optional[User] = PrivateAttr(default=None)

    @property
    def full_token(self) -> str:
        """Get full Redis key for session."""
        return USER_SESSION_KEY_PREFIX + self.token

    def initialize(self) -> Optional["Session"]:
        """
        Load session data from Redis.

        Returns:
            Self if session exists, None otherwise
        """
        session: Optional[dict] = redis_client.get_json(self.full_token)
        if session:
            self.user_id = session["user_id"]
            self.content = session["content"]
            self.expired = session["expired"]
            return self
        return None

    def create(self) -> "Session":
        """
        Create new session in Redis.

        Returns:
            Self for method chaining

        Raises:
            ConflictTokenError: If token already exists
        """
        created: Optional[Session] = self.initialize()
        if not created:
            redis_client.set_json(
                key=self.full_token, value=self.model_dump(), expire=SESSION_RENEWAL_AGE
            )
            return self
        raise ConflictTokenError(f"TOKEN: {self.token}")

    @property
    def is_accessable(self) -> bool:
        """Check if session is valid and not expired."""
        return bool(self.user_id and self.expired > dt.datetime.now().timestamp())

    def get_user(self) -> Optional[User]:
        """
        Retrieve user object from database.

        Returns:
            User object if exists, None otherwise
        """
        try:
            user: User = User.objects.get(id=self.user_id)
            self._user_obj = user
            return user
        except ObjectDoesNotExist:
            return None

    def update(self) -> "Session":
        """
        Update session data in Redis.

        Use case: Save modified session content.

        Returns:
            Self for method chaining
        """
        redis_client.set_json(
            key=self.full_token, value=self.model_dump(), expire=SESSION_RENEWAL_AGE
        )
        return self

    def clear(self) -> "Session":
        """
        Clear session content without flushing.

        Returns:
            Self for method chaining
        """
        self.content = {}
        redis_client.set_json(
            key=self.full_token, value=self.model_dump(), expire=SESSION_RENEWAL_AGE
        )
        return self

    def refresh(self) -> "Session":
        """
        Refresh session expiration in Redis.

        Use case: Extend session lifetime on each request.

        Returns:
            Self for method chaining
        """
        redis_client.set_json(
            key=self.full_token, value=self.model_dump(), expire=SESSION_RENEWAL_AGE
        )
        return self

    def flush(self) -> None:
        """Delete session from Redis."""
        redis_client.delete(key=self.full_token)


def get_all_sessions() -> Generator[Session, None, None]:
    """
    Enumerate all sessions from Redis.

    Yields:
        Session objects (not initialized)
    """
    redis_keys: Generator = redis_client.get_keys_by_prefix(
        prefix=USER_SESSION_KEY_PREFIX
    )

    for key in redis_keys:
        session_token: str = key.decode("utf-8")[len(USER_SESSION_KEY_PREFIX) :]
        session: Session = Session(token=session_token)
        yield session


def get_healthy_sessions() -> Generator[Session, None, None]:
    """
    Enumerate valid sessions with accessible users.

    Use case: Admin tools to list active user sessions.

    Yields:
        Initialized Session objects that are valid and have existing users
    """
    for s in get_all_sessions():
        session: Optional[Session] = s.initialize()
        if session and session.is_accessable and session.get_user():
            yield session
