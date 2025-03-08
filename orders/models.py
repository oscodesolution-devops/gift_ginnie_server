from django.db import models
from django.utils.timezone import now

class Order(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(("PENDING", "PENDING"), ("SHIPPED", "SHIPPED"), ("PROCESSING", "PROCESSING"), ("DELIVERED", "DELIVERED"), ("CANCELLED", "CANCELLED"), ("COMPLETED", "COMPLETED"), ("PAYMENT_FAILED", "PAYMENT_FAILED")))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    delivery_address = models.ForeignKey("users.CustomerAddress", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.user.id) + " - " + str(self.total_price)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order ID: {self.order.id})"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=10, choices=(("PERCENT", "PERCENT"), ("FLAT", "FLAT")))  # Percentage or flat discount
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_usage = models.PositiveIntegerField(null=True, blank=True)  # Global limit
    max_usage_per_user = models.PositiveIntegerField(null=True, blank=True)  # Per user limit

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return self.code

class CouponUsage(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coupon Usage"
        verbose_name_plural = "Coupon Usages"
        # unique_together = ("user", "coupon")

class Cart(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    coupon = models.ForeignKey("Coupon", null=True, blank=True, on_delete=models.SET_NULL, related_name="carts")

    def calculate_original_price(self):
        return sum(item.price for item in self.items.all())

    def calculate_discounted_price(self):
        total = sum(item.price for item in self.items.all()) # Total price without discount
        # Apply coupon discount if valid
        if (self.coupon and self.coupon.is_active and self.coupon.valid_from <= now() and self.coupon.valid_until >= now()):
            if self.coupon.discount_type == "PERCENT":
                total -= total * (self.coupon.discount_value / 100)
            elif self.coupon.discount_type == "FLAT":
                total -= self.coupon.discount_value
        return max(total, 0)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart for {self.user} with {self.items.count()} items"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price at the time of addition

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Cart ID: {self.cart.id})"