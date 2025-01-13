from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include("users.urls"),
    ),
    path(
        "api/v1/",
        include("products.urls"),
    ),
    # path(
    #     "api/v1/",
    #     include("orders.urls"),
    # ),
    # path(
    #     "api/v1/",
    #     include("payments.urls"),
    # ),
    # path(
    #     "api/v1/",
    #     include("ratings.urls"),
    # ),
    # path("api/v1/", include("core.urls")),
]
