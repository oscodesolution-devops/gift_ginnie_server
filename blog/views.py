from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import BlogPost, BlogComment
from .serializers import BlogPostSerializer, BlogComments

# BlogPost Views
class BlogPostListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"message": "Blog posts fetched successfully.", "data": response.data}, status=status.HTTP_200_OK)

class BlogPostDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"message": "Blog post fetched successfully.", "data": response.data}, status=status.HTTP_200_OK)

class BlogPostCreateView(CreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({"message": "Blog post created successfully.", "data": response.data}, status=status.HTTP_201_CREATED)

class BlogPostUpdateView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({"message": "Blog post updated successfully.", "data": response.data}, status=status.HTTP_200_OK)

class BlogPostDeleteView(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response({"message": "Blog post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# BlogComment Views
class BlogCommentListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BlogComments

    def get_queryset(self):
        return BlogComment.objects.filter(post_id=self.kwargs["post_id"])

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"message": "Comments fetched successfully.", "data": response.data}, status=status.HTTP_200_OK)

class BlogCommentCreateView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BlogComments

    def post(self, request, *args, **kwargs):
        request.data["post"] = self.kwargs["post_id"]
        response = super().post(request, *args, **kwargs)
        return Response({"message": "Comment created successfully.", "data": response.data}, status=status.HTTP_201_CREATED)

class BlogCommentDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BlogComment.objects.all()
    serializer_class = BlogComments
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"message": "Comment fetched successfully.", "data": response.data}, status=status.HTTP_200_OK)

class BlogCommentUpdateView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = BlogComment.objects.all()
    serializer_class = BlogComments
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({"message": "Comment updated successfully.", "data": response.data}, status=status.HTTP_200_OK)

class BlogCommentDeleteView(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = BlogComment.objects.all()
    serializer_class = BlogComments
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)