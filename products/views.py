from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from ratings.models import ProductRating
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Avg, Count, F, Q
from django.shortcuts import get_object_or_404
import cloudinary
import cloudinary.uploader
from .models import (
    CarouselItem,
    FavouriteProduct,
    Product,
    ProductCategory,
    ProductImage,
)
from .serializers import (
    AddProductImageSerializer,
    AddProductSerializer,
    CarouselItemSerializer,
    CategorySerializer,
    DeleteProductImagesSerializer,
    FavouriteProductSerializer,
    PopularCategorySerializer,
    PopularProductSerializer,
    ProductSerializer,
    UpdateProductSerializer,
)


class CarouselView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        carousel_items = CarouselItem.objects.filter(is_active=True)
        serializer = CarouselItemSerializer(carousel_items, many=True)
        return Response(
            {"message": "Top carousel fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if request.user.is_superuser or request.user.is_staff:
            try:
                serializer = CarouselItemSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "message": "Carousel item added successfully.",
                            "date": serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {
                            "message": "Carousel item not added.",
                            "data": serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def patch(self, request, id):
        if request.user.is_superuser or request.user.is_staff:
            try:
                if not request.data:
                    return Response(
                        {"message": "No data provided"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                carousel_item = CarouselItem.objects.get(id=id)
                serializer = CarouselItemSerializer(
                    carousel_item, data=request.data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "message": "Carousel item updated successfully.",
                            "data": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "message": "Carousel item not updated.",
                            "data": serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def delete(self, request, id):
        if request.user.is_superuser or request.user.is_staff:
            try:
                carousel_item = CarouselItem.objects.get(id=id)
                carousel_item.delete()
                return Response(
                    {"message": "Carousel item deleted successfully."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


class DeleteProductImagesView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        if request.user.is_superuser or request.user.is_staff:
            try:
                serializer = DeleteProductImagesSerializer(data=request.data)
                if serializer.is_valid():
                    product_image_ids = request.data.get("product_image_ids")
                    product_images = ProductImage.objects.filter(
                        id__in=product_image_ids
                    )
                    if not product_images:
                        return Response(
                            {"message": "No product image found"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    for product_image in product_images:
                        res = cloudinary.uploader.destroy(
                            product_image.image.public_id, invalidate=True
                        )
                        # print(res)
                        product_image.delete()
                    return Response(
                        {"message": "Product image deleted successfully"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"message": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


class PopularProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            popular_products = (
                Product.objects.prefetch_related("images")
                .all()
                .annotate(
                    average_rating=Avg("ratings__rating"),
                    total_reviews=Count("ratings"),
                )
                .select_related("category")
                .filter(ratings__rating__isnull=False)
                .order_by("-average_rating")[:10]
            )
            serializer = PopularProductSerializer(
                popular_products, many=True, context={"request": request}
            )
            return Response(
                {
                    "message": "Popular products fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Error occurred while fetching popular products {e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class PopularCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            popular_categories = (
                ProductRating.objects.values("product__category__id")
                .annotate(
                    category_id=F("product__category__id"),
                    category_name=F("product__category__name"),
                    average_rating=Avg("rating"),
                    total_reviews=Count("id"),
                    category_description=F("product__category__description"),
                    image=F("product__category__image"),
                )
                .order_by("-average_rating")[:10]
            )
            serializer = PopularCategorySerializer(popular_categories, many=True)
            return Response(
                {
                    "message": "Popular categories fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Error occurred while fetching popular categories {e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class AddProductView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        if request.user.is_superuser or request.user.is_staff:
            serializer = AddProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Product added successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {
                    "message": "Product not added.",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


class UpdateDeleteProductView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        if request.user.is_superuser or request.user.is_staff:
            if not request.data:
                return Response(
                    {"message": "No data provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                product = Product.objects.get(id=id)
                serializer = UpdateProductSerializer(
                    product, data=request.data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "message": "Product updated successfully",
                            "data": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "message": "Product not updated.",
                            "data": serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Exception as e:
                return Response(
                    {
                        "message": f"Product not updated.",
                        "data": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def delete(self, request, id):
        if request.user.is_superuser or request.user.is_staff:
            print(request.user.is_superuser)
            try:
                product = Product.objects.get(id=id)
                product.delete()
                return Response(
                    {
                        "message": "Product deleted successfully",
                        "data": None,
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
            except Product.DoesNotExist:
                return Response(
                    {
                        "message": "Product not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Product.DoesNotExist:
                return Response(
                    {
                        "message": "Product not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response(
                    {
                        "message": "Product not deleted.",
                        "data": e,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


class AddProductImagesView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        if request.user.is_superuser or request.user.is_staff:
            serializer = AddProductImageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Product images added successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {
                    "message": "Product image not added.",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


class AllProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(
                products, many=True, context={"request": request}
            )
            return Response(
                {
                    "message": "All products fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Error occurred while fetching all products {e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProductView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product, context={"request": request})
            return Response(
                {
                    "message": "Product fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Product.DoesNotExist:
            return Response(
                {
                    "message": "Product not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Error occurred while fetching product {e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class AllCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            query_set = ProductCategory.objects.all()
            serializer = CategorySerializer(query_set, many=True)
            return Response(
                {
                    "message": "All categories fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Error occurred while fetching all categories {e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            products = Product.objects.filter(category__id=id)
            category_exists = ProductCategory.objects.filter(id=id).exists()
            if not category_exists:
                return Response(
                    {"message": f"The category_id {id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = ProductSerializer(
                products, many=True, context={"request": request}
            )
            return Response(
                {
                    "message": "Category found",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Error occurred while fetching category {e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, id):
        if request.user.is_superuser or request.user.is_staff:
            try:
                category = ProductCategory.objects.get(id=id)
                if not category:
                    return Response(
                        {"message": f"The category_id {id} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                if category.image and category.image.public_id:
                    res = cloudinary.uploader.destroy(
                        category.image.public_id, invalidate=True
                    )
                    print("category image removed", res)
                category.delete()
                return Response(
                    {
                        "message": f"Category {category.name} deleted successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {
                        "message": f"Error occurred while deleting category {e}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def patch(self, request, id):
        if request.user.is_superuser or request.user.is_staff:
            try:
                category = ProductCategory.objects.get(id=id)
                if not category:
                    return Response(
                        {"message": f"The category_id {id} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                serializer = CategorySerializer(
                    category, data=request.data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "message": f"Category {serializer.data['name']} updated successfully",
                            "data": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "message": f"Error occurred while updating category",
                            "data": serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Exception as e:
                return Response(
                    {
                        "message": f"Error occurred while updating category {e}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


class CategoryViewCREATE(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        if request.user.is_superuser or request.user.is_staff:
            try:
                serializer = CategorySerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "message": f"Category {serializer.data['name']} created successfully",
                            "data": serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {
                            "message": f"Error occurred while creating category",
                            "data": serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Exception as e:
                return Response(
                    {
                        "message": f"Error occurred while creating category {e}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


class FavouriteProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            favourite_products = FavouriteProduct.objects.filter(user=user)
            serializer = FavouriteProductSerializer(
                favourite_products, many=True, context={"request": request}
            )
            return Response(
                {
                    "message": "Favourite products retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Error occurred while retrieving favourite products {e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request):
        try:
            product_id = request.data.get("id")
            serializer = FavouriteProductSerializer(
                data=request.data, context={"request": request}
            )

            if serializer.is_valid():
                product = Product.objects.get(id=product_id)
                if product:
                    user = request.user
                    favourite_product = FavouriteProduct.objects.filter(
                        user=user, product=product
                    )
                    if favourite_product:
                        favourite_product.delete()
                        return Response(
                            {
                                "message": f"Product {product.name} unfavourited successfully",
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        serializer = FavouriteProductSerializer(
                            data=request.data, context={"request": request}
                        )
                        favourite_product = FavouriteProduct(user=user, product=product)
                        favourite_product.save()
                    return Response(
                        {
                            "message": f"Product {product.name} favourited successfully",
                        },
                        status=status.HTTP_201_CREATED,
                    )

            else:
                return Response(
                    {"message": "Validation error", "data": serializer.errors}
                )
        except Product.DoesNotExist:
            return Response(
                {"message": "product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Error occurred while favouriting product {e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class SearchProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    search_fields = ["name", "description", "category__name"]
    filter_backends = [SearchFilter, OrderingFilter]
