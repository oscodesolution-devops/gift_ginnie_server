from rest_framework import serializers
from .models import ProductRating
from orders.models import Order, OrderItem
from products.models import Product


class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ["id", "product_id", "rating", "review", "user_id", "created_at"]
        read_only_fields = ["id", "created_at", "user_id"]
