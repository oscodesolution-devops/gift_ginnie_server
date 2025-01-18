from django.utils.timezone import now
from datetime import timezone
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from django.db.models import F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from orders.serializers import CartItemSerializer, CartSerializer
from products.models import Product
from .models import CouponUsage, Order, Cart, CartItem, Coupon


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                return Response(
                    {"message": "Cart not found."}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = CartSerializer(cart)
            return Response(
                {"message": "Cart fetched successfully.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"Error occurred while fetching cart {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Apply a coupon to the cart."""
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                return Response(
                    {"message": "Cart not found."}, status=status.HTTP_404_NOT_FOUND
                )

            coupon_code = request.data.get("code")
            if not coupon_code:
                return Response(
                    {"message": "Coupon code is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
            if not coupon:
                return Response(
                    {"message": "Invalid or inactive coupon."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the coupon is valid
            if coupon.valid_from > now() or coupon.valid_until < now():
                return Response(
                    {"message": "This coupon is not valid at this time."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check global usage limit
            global_usage_count = CouponUsage.objects.filter(coupon=coupon).count()
            if coupon.max_usage and global_usage_count >= coupon.max_usage:
                return Response(
                    {"message": "This coupon has reached its usage limit."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check per-user usage limit
            user_usage_count = CouponUsage.objects.filter(
                coupon=coupon, user=request.user
            ).count()
            if (
                coupon.max_usage_per_user
                and user_usage_count >= coupon.max_usage_per_user
            ):
                return Response(
                    {
                        "message": f"You have reached your usage limit for this coupon ({coupon.max_usage_per_user})."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply coupon to the cart
            CouponUsage.objects.create(user=request.user, coupon=coupon)
            cart.coupon = coupon
            cart.save()

            return Response(
                {
                    "message": "Coupon applied successfully.",
                    "data": {"coupon": coupon.code},
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Remove a coupon from the cart."""
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                return Response(
                    {"message": "Cart not found."}, status=status.HTTP_404_NOT_FOUND
                )

            if not cart.coupon:
                return Response(
                    {"message": "No coupon applied to the cart."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Remove coupon from the cart
            cart.coupon = None
            cart.save()

            # Optionally, delete the associated CouponUsage record
            CouponUsage.objects.filter(user=request.user, coupon=cart.coupon).delete()

            return Response(
                {"message": "Coupon removed from the cart successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add a new item to the cart."""
        # Get or create the user's cart
        try:
            user_cart, created = Cart.objects.get_or_create(user=request.user)

            data = request.data.copy()
            data["cart"] = user_cart.id
            existing_item = CartItem.objects.filter(
                cart=user_cart, product=data.get("product_id")
            ).first()
            product = Product.objects.get(id=data.get("product_id"))
            if existing_item:
                existing_item.quantity = F("quantity") + data.get("quantity")
                existing_item.price = product.price * existing_item.quantity
                existing_item.save()
                existing_item.refresh_from_db()
                serializer = CartItemSerializer(existing_item)
                return Response(
                    {"message": "Item Updated successfully", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            serializer = CartItemSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Item added to cart successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"message": "Failed to add item to cart.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": f"Error occurred while adding item to cart {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request, cart_item_id):
        """Update the quantity or price of an existing cart item."""
        try:
            # Retrieve the cart item
            if not request.data:
                return Response(
                    {"message": "No data provided."}, status=status.HTTP_400_BAD_REQUEST
                )
            cart_item = get_object_or_404(
                CartItem, id=cart_item_id, cart__user=request.user
            )

            serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Cart item updated successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Failed to update cart item.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"message": "Cart item does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": "Failed to update cart item.", "errors": e.args},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, cart_item_id):
        """Delete an item from the cart."""
        # Retrieve and delete the cart item
        cart_item = get_object_or_404(
            CartItem, id=cart_item_id, cart__user=request.user
        )
        cart_item.delete()
        return Response(
            {"message": "Item removed from cart successfully."},
            status=status.HTTP_200_OK,
        )
