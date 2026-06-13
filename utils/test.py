"""
Abstract base test classes.
"""

from typing import Literal

from django.contrib.auth.models import User
from pydantic import BaseModel, Field
from rest_framework.test import APITestCase

from utils.session import Session

__all__ = [
    "APITestCasePack",
    "APITestCaseModel",
    "WebAppAPITestCase",
]


class APITestCaseModel(BaseModel):
    input: dict = Field()
    output: dict = Field()
    expected_code: int = Field()


class APITestCasePack(BaseModel):
    title: str = Field()
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"] = Field()
    auth_required: bool = Field()
    cases: list[APITestCaseModel] = Field()


class WebAppAPITestCase(APITestCase):
    test_cases: list[APITestCasePack]
    base_url: str

    @staticmethod
    def _has_nested_json_value(data: dict) -> bool:
        return any(isinstance(value, (dict, list)) for value in data.values())

    def base_setUp(self):
        # Auth
        self.user = User.objects.create_user(
            username="09101234567", password="testpassword"
        )
        self.user.initial_action()
        auth_token = Session(user_id=self.user.pk).create().token
        self.auth_token = f"Bearer {auth_token}"

    def run_tests(self):
        for test_case in self.test_cases:
            self.request_loop(
                test_cases=test_case.cases,
                method=test_case.method,
                auth_required=test_case.auth_required,
            )

    def request_loop(
        self, test_cases: list[APITestCaseModel], method: str, auth_required: bool
    ):
        match method:
            case "POST":
                client_method = self.client.post
            case "PUT":
                client_method = self.client.put
            case "PATCH":
                client_method = self.client.patch
            case "DELETE":
                client_method = self.client.delete
            case _:
                client_method = self.client.get

        for test_case in test_cases:
            request_kwargs = {
                "HTTP_AUTHORIZATION": self.auth_token if auth_required else None,
            }
            if self._has_nested_json_value(test_case.input):
                request_kwargs["format"] = "json"

            response = client_method(self.base_url, test_case.input, **request_kwargs)
            self.assertEqual(response.status_code, test_case.expected_code)
            if "output" in test_case:
                self.assertEqual(response.data, test_case.output)
