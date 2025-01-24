from rest_framework import serializers
from .models import BlogPost, BlogComment


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = "__all__"
        read_only_fields = ["author", "created_at", "updated_at"]


class BlogComments(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "author", ""]
