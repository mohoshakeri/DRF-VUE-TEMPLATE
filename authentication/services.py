import random
from typing import Any, Optional

from CONSTANTS import (
    VERIFICATION_CODE_CACHE_AGE,
    VERIFICATION_CODE_CACHE_PREFIX,
    VERIFICATION_CODE_LENGTH,
)
from project.log import logger_set
from services.redis import redis_client
from services.sms import MockSmsService
from tools.converters import persian_english_converter
from tools.datetimes import dt
from utils.session import Session

from .models import *

logger = logger_set("authentication.services")


def normalize_mobile(mobile: str) -> str:
    return persian_english_converter(str(mobile).strip())


def get_verification_cache_key(mobile: str) -> str:
    return "{}{}".format(VERIFICATION_CODE_CACHE_PREFIX, mobile)


def generate_verification_code(length: int = VERIFICATION_CODE_LENGTH) -> str:
    start: int = 0
    end: int = (10**length) - 1
    random_number: int = random.SystemRandom().randint(start, end)
    return str(random_number).zfill(length)


def request_verification_code(
    mobile: str,
    sms_service: Optional[MockSmsService] = None,
) -> dict[str, Any]:
    mobile = normalize_mobile(mobile)
    code: str = generate_verification_code()
    sent_at: dt.datetime = dt.datetime.now()
    expire_at: dt.datetime = dt.datetime.now() + dt.timedelta(
        seconds=VERIFICATION_CODE_CACHE_AGE
    )
    cache_key: str = get_verification_cache_key(mobile)
    service: MockSmsService = sms_service or MockSmsService()
    gateway_response: dict = service.send_verification_code(mobile, code)

    cached_verification: dict[str, Any] = {
        "mobile": mobile,
        "code": code,
        "sent_at": sent_at.timestamp(),
        "expire_at": expire_at.timestamp(),
        "gateway_response": gateway_response,
    }
    redis_client.set_json(
        key=cache_key,
        value=cached_verification,
        expire=VERIFICATION_CODE_CACHE_AGE,
    )

    logger.info(
        msg={
            "message": "Verification code requested",
            "mobile": mobile,
        }
    )
    return {
        "mobile": mobile,
        "expire_at": expire_at,
        "expire_seconds": VERIFICATION_CODE_CACHE_AGE,
    }


def verify_mobile_code(mobile: str, code: str) -> Optional[User]:
    mobile = normalize_mobile(mobile)
    code = persian_english_converter(str(code).strip())
    cache_key: str = get_verification_cache_key(mobile)
    cached: Optional[dict] = redis_client.get_json(cache_key)

    if not cached:
        logger.warning(msg={"message": "Verification code missing", "mobile": mobile})
        return None

    if cached.get("expire_at", 0) < dt.datetime.now().timestamp():
        redis_client.delete(cache_key)
        logger.warning(msg={"message": "Verification code expired", "mobile": mobile})
        return None

    if cached.get("code") != code:
        logger.warning(msg={"message": "Verification code mismatch", "mobile": mobile})
        return None

    user: Optional[User] = User.objects.filter(mobile=mobile).first()
    if not user:
        user = User.objects.create_user(mobile=mobile)

    redis_client.delete(cache_key)
    logger.info(msg={"message": "Verification code accepted", "user_id": user.id})
    return user


def create_auth_token(user: User) -> str:
    return Session(user_id=user.id).create().token
