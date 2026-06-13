from typing import Any

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from utils.permissions import IsAuthenticated
from utils.session import Session
from utils.views import BaseView

from .serializers import *
from .services import create_auth_token, request_verification_code, verify_mobile_code


class RequestVerificationCodeView(BaseView):
    """
    POST -> Send Verification Code
    """

    permission_classes = [permissions.AllowAny]
    throttle_scope = "vcode"

    def post(self, request: Request) -> Response:
        serializer: RequestVerificationCodeSerializer = (
            RequestVerificationCodeSerializer(data=request.data)
        )
        if not serializer.is_valid():
            return Response(
                {
                    "message": "اطلاعات وارد شده صحیح نیست",
                    "devMessage": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification: dict = request_verification_code(
            serializer.validated_data["mobile"]
        )
        result_serializer: RequestVerificationCodeResultSerializer = (
            RequestVerificationCodeResultSerializer(verification)
        )
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class VerifyCodeView(BaseView):
    """
    POST -> Verify Code And Login
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        serializer: VerifyCodeSerializer = VerifyCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "اطلاعات وارد شده صحیح نیست",
                    "devMessage": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user: User | None = verify_mobile_code(
            mobile=serializer.validated_data["mobile"],
            code=serializer.validated_data["code"],
        )
        if not user:
            return Response(
                {"message": "کد تایید اشتباه یا منقضی شده است"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token: str = create_auth_token(user)
        output_serializer: AuthTokenSerializer = AuthTokenSerializer(
            {"token": token, "user": user}
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class CurrentUserView(BaseView):
    """
    GET -> Get Current User
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer: UserSerializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(BaseView):
    """
    POST -> Logout Current User
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        auth_session: Any = getattr(request, "auth_session", None)
        if isinstance(auth_session, Session):
            auth_session.flush()
        return Response(status=status.HTTP_204_NO_CONTENT)
