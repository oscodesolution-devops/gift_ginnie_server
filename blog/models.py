from django.db import models

# imoprt get user model
from django.contrib.auth import get_user_model

User = get_user_model()


class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField("date published", auto_now_add=True)
    updated_at = models.DateTimeField("date updated", auto_now=True)
    published = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    enable_comments = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"
        verbose_name_plural = "blog posts"
        verbose_name = "blog post"


class BlogComment(models.Model):
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.body

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"
        verbose_name_plural = "blog comments"
        verbose_name = "Blog Comment"
