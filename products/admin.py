from django.contrib import admin
from django.contrib.admin import register
from unfold.admin import ModelAdmin
from .models import Product, ProductCategory, ProductImage, CarouselItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # todo: Cloudary image logic to be implemented

@register(Product)
class ProductAdmin(ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ("name", "category", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("category", "created_at", "updated_at")

@register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("product__name", "image", "created_at", "updated_at")
    search_fields = ("product__name", "image")
    list_filter = ("product", "created_at", "updated_at")
    # todo: Cloudary image logic to be implemented

@register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ("name", "description", "image")
    search_fields = ("name","description")

@register(CarouselItem)
class CarouselItemAdmin(ModelAdmin):
    list_display = ("title", "description", "image", "created_at", "order", "is_active")
    search_fields = ("title", "description", "order")
    list_filter = ("created_at", "is_active")