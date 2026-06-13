from django.urls import path

from .views import *

urlpatterns = [
    path(
        "request-code/", RequestVerificationCodeView.as_view(), name="auth-request-code"
    ),
    path("verify-code/", VerifyCodeView.as_view(), name="auth-verify-code"),
    path("me/", CurrentUserView.as_view(), name="auth-me"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
]
