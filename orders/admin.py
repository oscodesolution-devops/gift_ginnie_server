from django.contrib import admin
from .models import CartItem, Coupon, Order, Cart


admin.site.register(Order)

admin.site.register(Cart)
admin.site.register(Coupon)
