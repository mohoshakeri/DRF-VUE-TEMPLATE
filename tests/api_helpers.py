from uuid import UUID

from authentication.models import User
from utils.test import APITestCaseModel, APITestCasePack

DUMMY_UUID = UUID("00000000-0000-0000-0000-000000000000")


class FakeRedisClient:
    def __init__(self):
        self.storage = {}

    def set_string(self, key, value, expire=None):
        self.storage[key] = str(value)

    def get_string(self, key):
        return self.storage.get(key)

    def set_json(self, key, value, expire=None):
        self.storage[key] = value

    def get_json(self, key):
        return self.storage.get(key)

    def set_int(self, key, value, expire=None):
        self.storage[key] = int(value)

    def get_int(self, key):
        value = self.storage.get(key)
        return int(value) if value is not None else None

    def delete(self, key):
        self.storage.pop(key, None)

    def get_keys_by_prefix(self, prefix):
        for key in list(self.storage):
            if key.startswith(prefix):
                yield key.encode("utf-8")


fake_redis_client = FakeRedisClient()


def install_fake_redis():
    import services.redis
    import utils.abstract
    import utils.session

    services.redis.redis_client = fake_redis_client
    utils.abstract.redis_client = fake_redis_client
    utils.session.redis_client = fake_redis_client


install_fake_redis()


def case(input=None, expected_code=200):
    return APITestCaseModel(input=input or {}, output={}, expected_code=expected_code)


def pack(title, method, auth_required, expected_code, input=None):
    return APITestCasePack(
        title=title,
        method=method,
        auth_required=auth_required,
        cases=[case(input=input, expected_code=expected_code)],
    )


def create_user(mobile="09101234567", name="کاربر تست", category=1):
    user = User.objects.create_user(mobile=mobile, password="testpassword")
    user.initial_action()
    user.info.name = name
    user.info.category = category
    user.info.save()
    return user
