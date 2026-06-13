"""
Security utilities for JWT token management.

This module provides functions for creating and decoding JWT tokens with expiration.
"""

from typing import Dict, Optional
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from tools.datetimes import dt


def create_token(key: str, data: Dict, expire_minutes: int) -> str:
    """
    Create a JWT token with expiration.

    Use case: Generate secure tokens for authentication and authorization.

    Process:
    1. Add expiration time to payload data
    2. Encode payload with HS256 algorithm
    3. Return signed token string

    Args:
        key: Secret key for signing the token
        data: Payload data to encode in the token
        expire_minutes: Token expiration time in minutes

    Returns:
        Encoded JWT token string
    """
    payload: Dict = {
        **data,
        "exp": dt.datetime.now() + dt.timedelta(minutes=expire_minutes),
    }
    token: str = jwt.encode(payload, key, algorithm="HS256")
    return token


def decode_token(key: str, token: str) -> Optional[Dict]:
    """
    Decode and verify a JWT token.

    Use case: Verify and extract data from authentication tokens.

    Process:
    1. Attempt to decode token using secret key
    2. Verify signature and expiration
    3. Return payload if valid, None if invalid or expired

    Args:
        key: Secret key used to sign the token
        token: JWT token string to decode

    Returns:
        Decoded payload dictionary if valid, None otherwise
    """
    try:
        decoded: Dict = jwt.decode(token, key, algorithms=["HS256"])
        return decoded
    except (ExpiredSignatureError, InvalidTokenError):
        return None
