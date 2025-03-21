from django.contrib.admin import register
from unfold.admin import ModelAdmin
from blog.models import BlogComment, BlogPost
from django.db import models
from unfold.contrib.forms.widgets import WysiwygWidget

@register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ['title', 'author', 'published', 'created_at', 'updated_at', 'enable_comments']
    search_fields = ["title", "body", "author__email"]
    list_filter = ["published", 'enable_comments', 'author', 'created_at', 'updated_at']
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}

@register(BlogComment)
class BlogCommentAdmin(ModelAdmin):
    list_display = ['post', 'author', 'created_at', 'updated_at']
    search_fields = ["post__title", "post__body", "author__email"]
    list_filter = ["author", "created_at", "updated_at"]
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}