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
        fields = ["id", "image", "product"]
        write_only_fields = ["product"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class PopularProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "images"]


class AddProductSerializer(serializers.ModelSerializer):
    description = serializers.CharField(max_length=100, required=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "category_id"]
        read_only_fields = ["id", "category"]
        write_only_fields = ["category_id"]

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
                raise serializers.ValidationError("A product must have at least 3 images.")

            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        


    def create(self, validated_data):
        """
        Creates `ProductImage` instances for the product.
        """
        try:
            product_id = self.initial_data.get("product_id")
            validated_data['product'] = Product.objects.get(id=product_id)
            images = validated_data["images"]

            product_images = []
            for image in images:
                product_images.append(ProductImage(product=product, image=image))
                print(product.name,product_images)
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

    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "category_id", "images"]
        read_only_fields = ["id", "category", "images"]
        write_only_fields = ["category_id"]



    def create(self, validated_data):
        validated_data["category"] = ProductCategory.objects.get(
            id=validated_data["category_id"]
        )
        validated_data.pop("category_id")
        return Product.objects.create(**validated_data)

class DeleteProductImagesSerializer(serializers.ModelSerializer):
    product_image_ids = serializers.ListField(child=serializers.IntegerField())
    class Meta:
        model = ProductImage
        fields = ["product_image_ids"]