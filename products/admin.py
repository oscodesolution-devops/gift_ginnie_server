from django.contrib import admin

from .models import Product, ProductCategory, ProductImage, CarouselItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("category", "created_at", "updated_at")

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image", "created_at", "updated_at")
    search_fields = ("product__name", "image")
    list_filter = ("product", "created_at", "updated_at")

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory)
admin.site.register(ProductImage ,ProductImageAdmin)
admin.site.register(CarouselItem)
