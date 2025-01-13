from django.urls import path
from .views import (
    SendOTPView,
    VerifyOTPView,
    UserProfileUpdateView,
    DummyTokenView,
    ProfileView,
    AddressView,
)


urlpatterns = [
    path("users/dummyToken/", DummyTokenView.as_view(), name="dummyToken"),
    path("users/auth/sendOTP/", SendOTPView.as_view(), name="sendOTP"),
    path("users/auth/verifyOTP/", VerifyOTPView.as_view(), name="verifyOTP"),
    path("users/profile/update/", UserProfileUpdateView.as_view(), name="user-profile"),
    path("users/profile/", ProfileView.as_view(), name="profile"),
    path("users/profile/address/", AddressView.as_view(), name="address"),
]
