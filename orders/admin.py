from django.contrib.admin import register
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from .models import CartItem, Coupon, CouponUsage, Order, Cart, OrderItem
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm

@register(Order)
class OrderAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ['user', 'status', 'total_price', 'discount_applied', 'final_price', 'updated_at', 'razorpay_order_id', 'razorpay_payment_id', 'delivery_address']
    search_fields = ["user__username", "status", "total_price", "discount_applied", "final_price", "updated_at", "razorpay_order_id", "razorpay_payment_id", "delivery_address__address"]
    list_filter = ["status", "updated_at"]

@register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ['order', 'product__name', 'quantity', 'price']
    search_fields = ["order__user__username", "product__name"]

@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ['user', 'coupon', 'calculate_original_price', 'calculate_discounted_price']
    search_fields = ["user__username", "coupon__code"]
    list_filter = ["coupon__is_active", "coupon__valid_from", "coupon__valid_until", "coupon__max_usage", "coupon__max_usage_per_user"]

@register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ['cart', 'product__name', 'quantity', 'price']
    search_fields = ["cart__user__username", "product__name"]

@register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_until', 'max_usage', 'max_usage_per_user']
    search_fields = ["code", "title", "description"]
    list_filter = ["is_active", "valid_from", "valid_until", "max_usage", "max_usage_per_user"]
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}

@register(CouponUsage)
class CouponUsageAdmin(ModelAdmin):
    list_display = ['user', 'coupon', 'used_at']
    search_fields = ["user__username", "coupon__code"]