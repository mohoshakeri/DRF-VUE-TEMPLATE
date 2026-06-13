from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import User
from authentication.services import get_verification_cache_key
from tests.api_helpers import fake_redis_client, install_fake_redis
from utils.session import Session


class AuthViewTest(APITestCase):
    request_code_url: str = "/api/v1/auth/request-code/"
    verify_code_url: str = "/api/v1/auth/verify-code/"
    me_url: str = "/api/v1/auth/me/"
    logout_url: str = "/api/v1/auth/logout/"
    mobile: str = "09101234567"

    def setUp(self) -> None:
        fake_redis_client.flush()
        install_fake_redis()

    def _request_code(self) -> dict:
        response = self.client.post(
            self.request_code_url,
            {"mobile": self.mobile},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cache_key: str = get_verification_cache_key(self.mobile)
        verification: dict = fake_redis_client.get_json(cache_key)
        self.assertIsNotNone(verification)
        return verification

    def _login(self) -> dict:
        verification: dict = self._request_code()
        response = self.client.post(
            self.verify_code_url,
            {
                "mobile": self.mobile,
                "code": verification["code"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data

    def test_request_code_stores_verification_in_redis(self) -> None:
        response = self.client.post(
            self.request_code_url,
            {"mobile": self.mobile},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["mobile"], self.mobile)
        cache_key: str = get_verification_cache_key(self.mobile)
        verification: dict = fake_redis_client.get_json(cache_key)
        self.assertEqual(verification["mobile"], self.mobile)
        self.assertEqual(verification["gateway_response"]["provider"], "mock")
        self.assertTrue(verification["gateway_response"]["is_mock"])

    def test_request_code_rejects_invalid_mobile(self) -> None:
        response = self.client.post(
            self.request_code_url,
            {"mobile": "123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("devMessage", response.data)
        self.assertEqual(fake_redis_client.storage, {})

    def test_verify_code_creates_user_and_token(self) -> None:
        verification: dict = self._request_code()
        response = self.client.post(
            self.verify_code_url,
            {
                "mobile": self.mobile,
                "code": verification["code"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["mobile"], self.mobile)
        self.assertTrue(User.objects.filter(mobile=self.mobile).exists())
        cache_key: str = get_verification_cache_key(self.mobile)
        self.assertIsNone(fake_redis_client.get_json(cache_key))

    def test_verify_code_rejects_wrong_code(self) -> None:
        self._request_code()
        response = self.client.post(
            self.verify_code_url,
            {
                "mobile": self.mobile,
                "code": "00000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertFalse(User.objects.filter(mobile=self.mobile).exists())
        cache_key: str = get_verification_cache_key(self.mobile)
        self.assertIsNotNone(fake_redis_client.get_json(cache_key))

    def test_me_returns_current_user(self) -> None:
        login_data: dict = self._login()
        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION="Bearer {}".format(login_data["token"]),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mobile"], self.mobile)

    def test_logout_flushes_session(self) -> None:
        login_data: dict = self._login()
        token: str = login_data["token"]
        logout_response = self.client.post(
            self.logout_url,
            HTTP_AUTHORIZATION="Bearer {}".format(token),
        )
        session = Session(token=token).initialize()

        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(session)

        me_response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION="Bearer {}".format(token),
        )
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)
