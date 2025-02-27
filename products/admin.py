from django.contrib import admin
from django.contrib.admin import register
from unfold.admin import ModelAdmin
from .models import Product, ProductCategory, ProductImage, CarouselItem

@register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name", "category", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("category", "created_at", "updated_at")

@register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("product", "image", "created_at", "updated_at")
    search_fields = ("product__name", "image")
    list_filter = ("product", "created_at", "updated_at")

@register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ("name", "description", "image")
    search_fields = ("name","description")

@register(CarouselItem)
class CarouselItemAdmin(ModelAdmin):
    list_display = ("title", "description", "image", "created_at", "order", "is_active")
    search_fields = ("title", "description", "order")
    list_filter = ("created_at", "is_active")