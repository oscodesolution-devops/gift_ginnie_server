from django import forms
from django.contrib import admin
from django.contrib.admin import register
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from .models import Product, ProductCategory, ProductImage, CarouselItem, GiftForYou

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # todo: Cloudinary image logic to be implemented

class ProductForm(forms.ModelForm):
    is_gift_for_you = forms.BooleanField(required=False, label="Add to Gifts for You")
    display_order = forms.IntegerField(required=False, label="Display Order", min_value=0)

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['is_gift_for_you'].initial = GiftForYou.objects.filter(product=self.instance).exists()
        self.fields['is_gift_for_you'].widget.attrs.update({'class': 'vCheckboxInput unfold-toggle'})

    def clean(self):
        cleaned_data = super().clean()
        is_gift_for_you = cleaned_data.get('is_gift_for_you')
        display_order = cleaned_data.get('display_order')

        if is_gift_for_you and display_order is None:
            raise forms.ValidationError("Display Order must be specified if 'Add to Gifts for You' is selected.")
        return cleaned_data

@register(Product)
class ProductAdmin(ModelAdmin):
    form = ProductForm
    inlines = [ProductImageInline]
    list_display = ("name", "category", "created_at", "updated_at", "get_is_gift_for_you")
    search_fields = ("name", "description")
    list_filter = ("category", "created_at", "updated_at")
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category', 'brand', 'original_price', 'selling_price', 'stock')
        }),
        ('Gifts for You', {
            'fields': ('is_gift_for_you', 'display_order'),
            'description': 'If you want this product to be a gift, select the checkbox and specify the display order.',
        }),
    )

    def get_is_gift_for_you(self, obj):
        return GiftForYou.objects.filter(product=obj).exists()
    get_is_gift_for_you.boolean = True
    get_is_gift_for_you.short_description = "Is Gift For You"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        is_gift_for_you = form.cleaned_data.get('is_gift_for_you')
        display_order = form.cleaned_data.get('display_order')

        if is_gift_for_you:
            gift_for_you, created = GiftForYou.objects.get_or_create(product=obj, defaults={'product_category': obj.category, 'display_order': display_order or 0})
            if not created and gift_for_you.display_order != (display_order or 0):
                gift_for_you.display_order = display_order or 0
                gift_for_you.save()
        else:
            GiftForYou.objects.filter(product=obj).delete()

    def get_inline_instances(self, request, obj=None):
        return super().get_inline_instances(request, obj)

@register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("product__name", "image", "created_at", "updated_at")
    search_fields = ("product__name", "image")
    list_filter = ("product", "created_at", "updated_at")
    # todo: Cloudinary image logic to be implemented

@register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ("name", "description", "image")
    search_fields = ("name", "description")
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}

@register(CarouselItem)
class CarouselItemAdmin(ModelAdmin):
    list_display = ("title", "description", "image", "created_at", "order", "is_active")
    search_fields = ("title", "description", "order")
    list_filter = ("created_at", "is_active")
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget,},}

@register(GiftForYou)
class GiftForYouAdmin(ModelAdmin):
    list_display = ("product_category", "product", "display_order")
    search_fields = ("product_category__name", "product__name")
    list_filter = ("product_category", "display_order")