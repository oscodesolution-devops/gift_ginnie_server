from datetime import datetime, timezone
from django.db import models
from cloudinary.models import CloudinaryField


class CarouselItem(models.Model):
    title = models.CharField(max_length=255)  # Title for the carousel item
    description = models.TextField(blank=True, null=True)  # Optional description
    imagelink = models.URLField(blank=True, null=True)  # Image for the carousel
    link = models.URLField(blank=True, null=True)  # Optional link for the item
    is_active = models.BooleanField(default=True)  # Only display active items
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    order = models.PositiveIntegerField(default=0)  # To control order of items

    class Meta:
        ordering = ["order"]
        verbose_name = "Carousel Item"
        verbose_name_plural = "Carousel Items"

    def __str__(self):
        return self.title


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField("product_category_image", blank=True, null=True)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True, related_name="images"
    )
    image = CloudinaryField("product_image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

