from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SendOTPView,
    VerifyOTPView,
    UserProfileUpdateView,
    DummyTokenView,
    ProfileView,
    AddressView,
)

urlpatterns = [
    path("users/dummyToken/<str:usertype>/", DummyTokenView.as_view(), name="dummyToken"),
    path("users/auth/tokens/refresh/", TokenRefreshView.as_view(), name="refreshToken"),
    path("users/auth/sendOTP/", SendOTPView.as_view(), name="sendOTP"),
    path("users/auth/verifyOTP/", VerifyOTPView.as_view(), name="verifyOTP"),
    path("users/profile/update/", UserProfileUpdateView.as_view(), name="user-profile"),
    path("users/profile/", ProfileView.as_view(), name="profile"),
    path("users/profile/address/", AddressView.as_view(), name="address"),
]