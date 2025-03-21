from django.contrib.admin import register
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from .models import ProductRating

@register(ProductRating)
class ProductRatingAdmin(ModelAdmin):
    list_display = ['product', 'rating', 'review', 'user']
    search_fields = ["product__name", "review", "user__username"]
    list_filter = ["rating", "review", "user"]
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}