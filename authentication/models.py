from typing import Any, Optional

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from project.log import logger_set
from tools.converters import add_YE_to_persian_name
from utils.db import *
from utils.validators import *

logger = logger_set("authentication.model")

__all__ = [
    "User",
]


class _UserManager(BaseUserManager):
    def create_user(
        self, mobile: str, password: Optional[str] = None, **extra_fields: Any
    ) -> "User":
        if not mobile:
            raise ValueError("Mobile Is Required")

        user = self.model(mobile=mobile, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Disable Password Login

        user.save(using=self._db)
        user.initial_action()
        return user

    def create_superuser(
        self, mobile: str, password: str, **extra_fields: Any
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(mobile, password, **extra_fields)


class User(AbstractModel, AbstractBaseUser, PermissionsMixin):
    mobile: str = models.CharField(
        verbose_name="mobile",
        max_length=11,
        unique=True,
        validators=[MobileValidtor()],
    )

    is_active: bool = models.BooleanField(verbose_name="active", default=True)
    is_staff: bool = models.BooleanField(verbose_name="staff", default=False)

    name: Optional[str] = models.CharField(
        verbose_name="name",
        max_length=150,
        validators=[FullPersianLetterValidator()],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    objects = _UserManager()

    USERNAME_FIELD = "mobile"

    def get_full_name(self):
        return self.name or self.mobile

    def __str__(self) -> str:
        return self.mobile

    @property
    def dialog_name(self) -> str:
        if not self.name:
            return self.mobile
        name: str = self.name
        return add_YE_to_persian_name(name)

    def initial_action(self) -> None:
        pass
