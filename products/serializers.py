from rest_framework import serializers
from django.db.models import Avg, Count
from giftginnie.global_serializers import CloudinaryImage
from ratings.models import ProductRating
from .models import CarouselItem, Product, ProductCategory, ProductImage


class PopularCategorySerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    image = CloudinaryImage()
    category_name = serializers.CharField()
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    category_description = serializers.CharField()
    


class CarouselItemSerializer(serializers.ModelSerializer):
    image = CloudinaryImage()

    class Meta:
        model = CarouselItem
        fields = ["id", "title", "description", "image", "link"]


class CategorySerializer(serializers.ModelSerializer):
    image = CloudinaryImage()

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "description", "image"]


class ProductImageSerializer(serializers.ModelSerializer):
    image = CloudinaryImage()
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class PopularProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "category", "images"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(), source="category", write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "category_id", "images"]
        read_only_fields = ["id", "category", "images"]
        write_only_fields = ["category_id"]

    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj)
        return ProductImageSerializer(images, many=True).data

    def create(self, validated_data):
        validated_data["category"] = ProductCategory.objects.get(
            id=validated_data["category_id"]
        )
        validated_data.pop("category_id")
        return Product.objects.create(**validated_data)
