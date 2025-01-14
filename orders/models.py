from django.db import models


class Order(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=(
            ("PENDING", "PENDING"),
            ("DELIVERED", "DELIVERED"),
            ("CANCELLED", "CANCELLED"),
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_address = models.ForeignKey(
        "users.CustomerAddress", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.product.name + " - " + str(self.quantity)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=10, choices=(("PERCENT", "PERCENT"), ("FLAT", "FLAT"))
    )  # Percentage or flat discount
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return self.code


class Cart(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(
        "Coupon", null=True, blank=True, on_delete=models.SET_NULL
    )

    def calculate_total_price(self):
        # Total price without discount
        total = sum(item.quantity * item.price for item in self.items.all())

        # Apply coupon discount if valid
        if self.coupon:
            if self.coupon.discount_type == "PERCENT":
                total -= total * (self.coupon.discount_value / 100)
            elif self.coupon.discount_type == "FLAT":
                total -= self.coupon.discount_value

        return max(total, 0)  # Ensure the total doesn't go below 0

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return self.product.name + " - " + str(self.quantity)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Product price at the time of addition

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Cart ID: {self.cart.id})"
