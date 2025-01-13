from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ratings.models import ProductRating
from django.db.models import Avg, Count, F, Q
from .models import CarouselItem, Product, ProductCategory, ProductImage
from .serializers import (
    CarouselItemSerializer,
    CategorySerializer,
    PopularCategorySerializer,
    PopularProductSerializer,
    ProductSerializer,
)


class CarouselView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carousel_items = CarouselItem.objects.filter(is_active=True)
        serializer = CarouselItemSerializer(carousel_items, many=True)
        return Response(
            {"message": "Top carousel fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class PopularProductsView(APIView):
    permissiono_classes = [IsAuthenticated]

    def get(self, request):
        try:
            popular_products = (
                Product.objects.prefetch_related("images")
                .all()
                .annotate(
                    average_rating=Avg("productrating__rating"),
                    total_reviews=Count("productrating__id"),
                )
                .select_related("category")
                .filter(productrating__rating__isnull=False)
                .order_by("-average_rating")[:10]
            )
            serializer = PopularProductSerializer(popular_products, many=True)
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
    permission_classes = [IsAuthenticated]

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


class AllProductsView(APIView):
    permission_classes = [IsAuthenticated]

    # def post(self, request):

    #     serializer = ProductSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(
    #             {
    #                 "message": "Product added successfully.",
    #                 "data": serializer.data,
    #             },
    #             status=status.HTTP_201_CREATED,
    #         )
    #     return Response(
    #         {
    #             "message": "Product not added.",
    #             "data": serializer.errors,
    #         },
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
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
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product)
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
    permission_classes = [IsAuthenticated]

    def get(self,request):
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
