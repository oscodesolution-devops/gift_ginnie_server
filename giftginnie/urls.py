from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="GifyGinnie API",
        default_version="v1",
        description="Api docs for GiftGinnie",
        terms_of_service="",
        contact=openapi.Contact(email="atharwani001@gmail.com"),
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)


urlpatterns = [
    re_path(
        r"^playground/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^docs/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include("users.urls"),
    ),
    path(
        "api/v1/",
        include("products.urls"),
    ),
    path(
        "api/v1/",
        include("orders.urls"),
    ),
    path(
        "api/v1/",
        include("ratings.urls"),
    ),
    path("api/v1/", include("blog.urls")),
]

admin.site.site_header = "GiftGinnie Admin"
admin.site.site_title = "GiftGinnie Admin"
admin.site.index_title = "GiftGinnie Admin"
