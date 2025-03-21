from django import forms
from django.contrib import admin
from django.contrib.admin import register
from django.db import models
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget
from .models import Product, ProductCategory, ProductImage, CarouselItem, GiftForYou

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    # todo: Cloudinary image logic to be implemented

@register(Product)
class ProductAdmin(ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ("name", "category", "created_at", "updated_at", "is_gift")
    search_fields = ("name", "description")
    list_filter = ("category", "created_at", "updated_at")
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}

@register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("product__name", "image", "created_at", "updated_at")
    search_fields = ("product__name", "image")
    list_filter = ("product", "created_at", "updated_at")
    # todo: Cloudinary image logic to be implemented

@register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ("name", "description", "image")
    search_fields = ("name", "description")
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}

@register(CarouselItem)
class CarouselItemAdmin(ModelAdmin):
    list_display = ("title", "description", "image", "created_at", "order", "is_active")
    search_fields = ("title", "description", "order")
    list_filter = ("created_at", "is_active")
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}

@register(GiftForYou)
class GiftForYouAdmin(ModelAdmin):
    list_display = ("product_category", "product", "display_order")
    search_fields = ("product_category__name", "product__name")
    list_filter = ("product_category", "display_order")