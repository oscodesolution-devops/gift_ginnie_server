from django.contrib import admin

from .models import Product, ProductCategory, ProductImage, CarouselItem

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductImage)
admin.site.register(CarouselItem)
