from django.contrib import admin
from .models import CartItem, Coupon, Order, Cart, OrderItem


admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(CartItem)
