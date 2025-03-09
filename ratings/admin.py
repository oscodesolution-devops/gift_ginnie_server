from django.contrib.admin import register
from unfold.admin import ModelAdmin
from .models import ProductRating

@register(ProductRating)
class ProductRatingAdmin(ModelAdmin):
    list_display = ['product', 'rating', 'review', 'user']
    search_fields = ["product__name", "review", "user__username"]
    list_filter = ["rating", "review", "user"]