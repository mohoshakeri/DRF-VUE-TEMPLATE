from typing import Any

from rest_framework import serializers

from CONSTANTS import VERIFICATION_CODE_LENGTH
from tools.converters import persian_english_converter
from utils.validators import MobileValidtor

from .models import *


class _NormalizeDigitsSerializer(serializers.Serializer):
    digit_fields: list[str] = []

    def to_internal_value(self, data: Any) -> dict:
        normalized_data: dict = dict(data)
        for field in self.digit_fields:
            if field in normalized_data:
                normalized_data[field] = persian_english_converter(
                    str(normalized_data[field]).strip()
                )
        return super().to_internal_value(normalized_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: list[str] = ["mobile", "name"]
        read_only_fields: list[str] = fields


class RequestVerificationCodeSerializer(_NormalizeDigitsSerializer):
    digit_fields: list[str] = ["mobile"]
    mobile = serializers.CharField(max_length=11, validators=[MobileValidtor()])


class RequestVerificationCodeResultSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    expire_at = serializers.DateTimeField()
    expire_seconds = serializers.IntegerField()


class VerifyCodeSerializer(_NormalizeDigitsSerializer):
    digit_fields: list[str] = ["mobile", "code"]
    mobile = serializers.CharField(max_length=11, validators=[MobileValidtor()])
    code = serializers.CharField(
        min_length=VERIFICATION_CODE_LENGTH,
        max_length=VERIFICATION_CODE_LENGTH,
    )

    def validate_code(self, value: str) -> str:
        if not value.isdigit():
            raise serializers.ValidationError("Code must contain digits only.")
        return value


class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserSerializer()
