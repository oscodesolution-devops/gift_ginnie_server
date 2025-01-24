from rest_framework import serializers

from orders.models import Cart, CartItem, Coupon, Order, OrderItem
from products.models import Product
from django.db import models
from products.serializers import ProductSerializer
from ratings.models import ProductRating
from users.serializers import CustomerAddressSerializer


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "title",
            "description",
            "discount_type",
            "discount_value",
            "max_usage",
            "max_usage_per_user",
            "valid_from",
            "valid_until",
            "is_active",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "product",
            "product_id",
            "quantity",
            "price",
        ]
        read_only_fields = ["id", "price"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_serializer = ProductSerializer(instance.product, context=self.context)
        representation["product"] = product_serializer.data
        return representation

    def create(self, validated_data):
        product = validated_data.get("product")
        validated_data["price"] = product.selling_price * validated_data["quantity"]
        # Call the parent class's `create` method
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.price = instance.product.selling_price * validated_data["quantity"]
        return super().update(instance, validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    coupon = CouponSerializer(read_only=True)
    total_items = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "coupon",
            "total_items",
            "original_price",
            "discounted_price",
            "discount_percentage",
        ]

    def get_total_items(self, obj):
        qty = obj.items.aggregate(qty=models.Sum("quantity"))["qty"]
        return qty

    def get_discounted_price(self, obj):
        return obj.calculate_discounted_price()

    def get_original_price(self, obj):
        return obj.calculate_original_price()

    def get_discount_percentage(self, obj):
        difference = obj.calculate_original_price() - obj.calculate_discounted_price()
        if difference == 0:
            return 0
        percentage = (difference / obj.calculate_original_price()) * 100
        return percentage


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    my_rating = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "my_rating"]
        read_only_fields = ["my_rating"]

    def get_my_rating(self, obj):
        rating = ProductRating.objects.filter(user=self.context["request"].user,product=obj.product).first()
        if rating:
            return rating.rating
        return None
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = CustomerAddressSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "discount_applied",
            "final_price",
            "created_at",
            "updated_at",
            "delivery_address",
            "items",
        ]
        read_only_fields = [
            "id",
            "status",
            "total_price",
            "discount_applied",
            "final_price",
            "created_at",
            "updated_at",
            "delivery_address",
            "items",
        ]
    

class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_payment_id = serializers.CharField(max_length=100)
    razorpay_order_id = serializers.CharField(max_length=100)
    razorpay_signature = serializers.CharField(max_length=100)

    def validate_razorpay_order_id(self, value):
        try:
            order = Order.objects.get(
                razorpay_order_id=value, user=self.context["request"].user
            )
            if order.status == "COMPLETED":
                raise serializers.ValidationError("Payment Order already completed")
        except Order.DoesNotExist:
            raise serializers.ValidationError("Payment Order does not exist")
        return value
