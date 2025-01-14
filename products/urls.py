from django.urls import path
from .views import (
    AddProductImagesView,
    AddProductView,
    AllCategoriesView,
    AllProductsView,
    CarouselView,
    DeleteProductImagesView,
    PopularCategoriesView,
    ProductView,
    PopularProductsView,
)


urlpatterns = [
    path("products/add/", AddProductView.as_view(), name="add-product"),
    path(
        "products/add/images/",
        AddProductImagesView.as_view(),
        name="add-product-images",
    ),
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
    path("products/deleteImages/",DeleteProductImagesView.as_view() ,name="delete-images"),
    # path("products/categories/deleteImages/", name="delete-images-categories"),
    path("products/carausel-items/", CarouselView.as_view(), name="carousel-items"),
    path("products/<int:id>/", ProductView.as_view(), name="product-detail"),
    path("products/", AllProductsView.as_view(), name="all-products"),
    path("products/categories/", AllCategoriesView.as_view(), name="all-categories"),
]
