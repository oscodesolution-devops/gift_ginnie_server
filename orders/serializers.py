from rest_framework import serializers

from orders.models import Cart, CartItem, Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "discount_type",
            "discount_value",
            "valid_from",
            "valid_until",
            "is_active",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "price"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    coupon = CouponSerializer(read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "coupon", "total_items", "total_price"]

    def get_total_items(self, obj):
        return obj.items.count()

    def get_total_price(self, obj):
        return obj.calculate_total_price()
