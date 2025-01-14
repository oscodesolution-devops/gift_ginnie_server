from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from orders.serializers import CartSerializer
from .models import Order, Cart, CartItem, Coupon


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            serializer = CartSerializer(cart)
            return Response(
                {
                    "message": "Cart fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Cart not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Cart added successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "message": "Cart not added.",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
