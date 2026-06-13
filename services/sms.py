from project.log import logger_set

logger = logger_set("services.sms")


class MockSmsService:
    provider_name: str = "mock"

    def send_verification_code(self, mobile: str, code: str) -> dict:
        message: str = "کد تایید شما: {}".format(code)
        payload: dict = {
            "provider": self.provider_name,
            "mobile": mobile,
            "message": message,
            "is_mock": True,
        }
        logger.info(
            msg={
                "message": "Mock SMS sent",
                "mobile": mobile,
                "provider": self.provider_name,
                "code": code,
            }
        )
        return payload
