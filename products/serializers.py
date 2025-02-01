from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.db.models import Avg, Count
from giftginnie.global_serializers import CloudinaryImage
from ratings.models import ProductRating
from .models import (
    CarouselItem,
    FavouriteProduct,
    Product,
    ProductCategory,
    ProductImage,
)
import cloudinary
import cloudinary.uploader


class PopularCategorySerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    image = CloudinaryImage()
    category_name = serializers.CharField()
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    category_description = serializers.CharField()


class CarouselItemSerializer(serializers.ModelSerializer):
    image = CloudinaryImage(read_only=True)
    carausel_image = serializers.ImageField(write_only=True)

    class Meta:
        model = CarouselItem
        fields = [
            "id",
            "title",
            "description",
            "image",
            "link",
            "carausel_image",
            "is_active",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        validated_data["image"] = validated_data.pop("carausel_image")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "carausel_image" in validated_data:
            if instance.image:
                res = cloudinary.uploader.destroy(
                    instance.image.public_id, invalidate=True
                )
                print("carousel image removed", res)
            validated_data["image"] = validated_data.pop("carausel_image")
        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    image = CloudinaryImage(read_only=True)
    category_image = serializers.ImageField(write_only=True)

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "description", "image", "category_image"]
        read_only_fields = ["id", "image"]

    def create(self, validated_data):
        validated_data["image"] = validated_data.pop("category_image")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "category_image" in validated_data:
            if instance.image:
                res = cloudinary.uploader.destroy(
                    instance.image.public_id, invalidate=True
                )
                print("Category image removed:", res)

            # Replace the `image` field with the new one
            instance.image = validated_data.pop("category_image")

        # Update other fields
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        return instance


class ProductImageSerializer(serializers.ModelSerializer):
    image = CloudinaryImage()
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "product"]
        write_only_fields = ["product"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class PopularProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "images", "is_liked"]

    def get_is_liked(self, obj):
        return FavouriteProduct.objects.filter(
            user=self.context["request"].user, product=obj
        ).exists()


class AddProductSerializer(serializers.ModelSerializer):
    description = serializers.CharField(max_length=100, required=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    in_stock = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_id",
            "original_price",
            "selling_price",
            "images",
            "stock",
            "in_stock",
            "rating",
            "brand",
            "product_type",
        ]
        read_only_fields = ["id", "category", "in_stock", "rating", "images"]
        write_only_fields = ["category_id", "stock"]

    def get_in_stock(self, obj):
        return obj.in_stock()

    def get_rating(self, obj):
        return obj.average_rating()

    def create(self, validated_data):
        try:
            validated_data["category"] = ProductCategory.objects.get(
                id=validated_data["category_id"]
            )
            validated_data.pop("category_id")
            product = Product.objects.create(**validated_data)

            return product
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError("Category does not exist")
        except Exception as e:
            raise serializers.ValidationError(e)


class UpdateProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(), source="category", write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_id",
            "images",
            "original_price",
            "selling_price",
            "stock",
            "brand",
            "product_type",
        ]
        read_only_fields = ["id", "category", "images"]
        write_only_fields = ["category_id"]

    def update(self, instance, validated_data):
        if "category_id" in validated_data:
            validated_data["category"] = ProductCategory.objects.get(
                id=validated_data["category_id"]
            )
            validated_data.pop("category_id")
        return super().update(instance, validated_data)


class AddProductImageSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    def validate_images(self, value):
        """
        Validates the images field for constraints:
        - Check if product already has existing images.
        - Ensure the new images meet the 3 to 6 count requirement.
        """

        global product
        # Ensure images are provided
        if not value:
            raise serializers.ValidationError("Images are required.")

        # Get the product from `initial_data` for validation
        product_id = self.initial_data.get("product_id")
        if not product_id:
            raise serializers.ValidationError("Product ID is required.")

        try:
            product = Product.objects.get(id=product_id)
            # Count existing images for the product
            existing_images_count = ProductImage.objects.filter(product=product).count()

            # Ensure total images do not exceed the limit
            total_images = existing_images_count + len(value)
            if total_images > 6:
                raise serializers.ValidationError(
                    f"Adding these images exceeds the limit. {6 - existing_images_count} more images allowed."
                )
            if total_images < 3:
                raise serializers.ValidationError(
                    "A product must have at least 3 images."
                )

            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")

    def create(self, validated_data):
        """
        Creates `ProductImage` instances for the product.
        """
        try:
            product_id = self.initial_data.get("product_id")
            validated_data["product"] = Product.objects.get(id=product_id)
            images = validated_data["images"]

            product_images = []
            for image in images:
                product_images.append(ProductImage(product=product, image=image))
            ProductImage.objects.bulk_create(product_images)

            return product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(), source="category", write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    in_stock = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_id",
            "images",
            "in_stock",
            "rating",
            "original_price",
            "selling_price",
            "brand",
            "product_type",
            "is_liked",
        ]
        read_only_fields = ["id", "category", "images", "is_liked"]
        write_only_fields = ["category_id"]

    def get_in_stock(self, obj):
        return obj.in_stock()

    def get_rating(self, obj):
        return obj.average_rating()

    def get_is_liked(self, obj):
        if self.context['request'].user.is_authenticated:
            return FavouriteProduct.objects.filter(
                user=self.context["request"].user, product=obj
            ).exists()
        return None

    def create(self, validated_data):
        validated_data["category"] = ProductCategory.objects.get(
            id=validated_data["category_id"]
        )
        validated_data.pop("category_id")
        product = Product.objects.create(**validated_data)
        return product


class DeleteProductImagesSerializer(serializers.ModelSerializer):
    product_image_ids = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = ProductImage
        fields = ["product_image_ids"]


class FavouriteProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = FavouriteProduct
        fields = ["id", "product"]
        read_only_fields = ["product"]
