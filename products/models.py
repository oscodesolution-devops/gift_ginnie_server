from datetime import datetime, timezone
from django.db import models
from cloudinary.models import CloudinaryField


class CarouselItem(models.Model):
    title = models.CharField(max_length=255)  # Title for the carousel item
    description = models.TextField(blank=True, null=True)  # Optional description
    image = CloudinaryField("carausel_image")  # Image for the carousel
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
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    product_type = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def in_stock(self):
        return self.stock > 0

    def average_rating(self):
        ratings = self.ratings.all()
        average_rating = ratings.aggregate(models.Avg("rating"))
        return average_rating["rating__avg"]


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


class FavouriteProduct(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="favourite_products"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="favourites"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Favourite Product"
        verbose_name_plural = "Favourite Products"

    def __str__(self):
        return self.product.name
