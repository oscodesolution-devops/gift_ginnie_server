from django.shortcuts import render
from orders.models import Order, OrderItem
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from products.models import Product
from ratings.serializers import ProductRatingSerializer
from .models import ProductRating

class RatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        try:
            user = request.user
            can_rate = (
                OrderItem.objects.select_related("order")
                .filter(order__user_id=user.id, product_id=product_id, order__status="DELIVERED",)
                .exists())
            product = Product.objects.get(id=product_id)
            rating = ProductRating.objects.filter(product=product)
            serializer = ProductRatingSerializer(rating, many=True)
            return Response({"message": "Product rating fetched successfully.", "data": {"ratings": serializer.data, "average_rating": product.average_rating(), "can_rate": can_rate}}, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"message": f"Error occurred while fetching product rating {e}"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, product_id):
        try:
            user = request.user
            can_rate = (
                OrderItem.objects.select_related("order")
                .filter(order__user_id=user.id, product_id=product_id, order__status="DELIVERED")
                .exists())
            if not can_rate:
                return Response({"message": "You cannot rate this product, you have not bought it yet."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProductRatingSerializer(data=request.data, context={"request": request, "product_id": product_id})
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Product rated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, product_id):
        try:
            user = request.user
            can_rate = (
                OrderItem.objects.select_related("order")
                .filter(order__user_id=user.id, product_id=product_id, order__status="DELIVERED")
                .exists())

            if not can_rate:
                return Response({"message": "You cannot rate this product, you have not bought it yet."}, status=status.HTTP_400_BAD_REQUEST)
            rating = ProductRating.objects.filter(product_id=product_id, user_id=user.id).first()
            serializer = ProductRatingSerializer(rating, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Product rating updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)