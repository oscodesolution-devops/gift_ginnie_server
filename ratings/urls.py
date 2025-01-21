from django.urls import path
from .views import RatingView

urlpatterns = [
    path(
        "product/<int:product_id>/rating/", RatingView.as_view(), name="product-rating"
    ),
]
