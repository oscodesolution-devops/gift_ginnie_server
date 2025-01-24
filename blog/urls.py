from django.urls import path
from .views import (
    BlogPostListView,
    BlogPostDetailView,
    BlogPostCreateView,
    BlogPostUpdateView,
    BlogPostDeleteView,
    BlogCommentListView,
    BlogCommentCreateView,
    BlogCommentDetailView,
    BlogCommentUpdateView,
    BlogCommentDeleteView,
)

urlpatterns = [
    path("blog-posts/", BlogPostListView.as_view(), name="blogpost-list"),
    path("blog-posts/create/", BlogPostCreateView.as_view(), name="blogpost-create"),
    path("blog-posts/<int:id>/", BlogPostDetailView.as_view(), name="blogpost-detail"),
    path(
        "blog-posts/<int:id>/update/",
        BlogPostUpdateView.as_view(),
        name="blogpost-update",
    ),
    path(
        "blog-posts/<int:id>/delete/",
        BlogPostDeleteView.as_view(),
        name="blogpost-delete",
    ),
    # BlogComment URLs
    path(
        "blog-posts/<int:post_id>/comments/",
        BlogCommentListView.as_view(),
        name="blogcomment-list",
    ),
    path(
        "blog-posts/<int:post_id>/comments/create/",
        BlogCommentCreateView.as_view(),
        name="blogcomment-create",
    ),
    path(
        "comments/<int:id>/", BlogCommentDetailView.as_view(), name="blogcomment-detail"
    ),
    path(
        "comments/<int:id>/update/",
        BlogCommentUpdateView.as_view(),
        name="blogcomment-update",
    ),
    path(
        "comments/<int:id>/delete/",
        BlogCommentDeleteView.as_view(),
        name="blogcomment-delete",
    ),
]
