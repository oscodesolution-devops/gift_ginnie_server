from django.urls import path
from .views import (
    AllCategoriesView,
    AllProductsView,
    CarouselView,
    PopularCategoriesView,
    ProductView,
    PopularProductsView,
)


urlpatterns = [
    path(
        "products/popular-products/",
        PopularProductsView.as_view(),
        name="popular-products",
    ),
    path(
        "products/popular-categories/",
        PopularCategoriesView.as_view(),
        name="popular-categories",
    ),
    path("products/carausel-items/", CarouselView.as_view(), name="carousel-items"),
    path("products/<int:id>/", ProductView.as_view(), name="product-detail"),
    path("products/", AllProductsView.as_view(), name="all-products"),
    path("products/categories/", AllCategoriesView.as_view(), name="all-categories"),
]
