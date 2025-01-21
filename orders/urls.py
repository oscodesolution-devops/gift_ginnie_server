from django.urls import path
from .views import (
    ApplyCouponView,
    CartItemView,
    CartView,
    CheckoutView,
    CouponView,
    VerifyPaymentView,
)

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("coupon/", CouponView.as_view(), name="coupon"),
    path("cart/item/", CartItemView.as_view(), name="cart-item-create"),
    path(
        "cart/item/<int:cart_item_id>/",
        CartItemView.as_view(),
        name="cart-item-update-delete",
    ),
    path("cart/applyCoupon/", ApplyCouponView.as_view(), name="apply-remove-coupon"),
    path("orders/checkout/", CheckoutView.as_view(), name="checkout"),
    path("orders/verifyPayment/", VerifyPaymentView.as_view(), name="verify-payment"),
]
