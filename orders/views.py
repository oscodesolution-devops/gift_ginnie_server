import json
from django.conf import settings
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
import razorpay
from rest_framework.response import Response
from django.db.models import F
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from orders.serializers import (
    CartItemSerializer,
    CartSerializer,
    CouponSerializer,
    OrderSerializer,
    VerifyPaymentSerializer,
)
from products.models import Product
from users.models import CustomerAddress
from .models import CouponUsage, Order, Cart, CartItem, Coupon, OrderItem


class CouponView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            coupon = Coupon.objects.filter(is_active=True)
            if not coupon:
                return Response(
                    {"message": "Coupon not found."}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = CouponSerializer(coupon, many=True, context={"request": request})
            return Response(
                {"message": "Coupons fetched successfully.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"Error: {e}"}, status=status.HTTP_400_BAD_REQUEST
            )


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                return Response(
                    {"message": "Cart not found."}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = CartSerializer(cart, context={"request": request})
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
                    {"message": "This coupon is expired."},
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
            if cart.items.count() == 0:
                return Response(
                    {"message": "Cart is empty, add items before applying coupon."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            usage = CouponUsage.objects.filter(user=request.user, coupon=coupon).first()
            if usage:
                return Response(
                    {
                        "message": "You cannot apply the same coupon twice."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
                existing_item.price = product.selling_price * existing_item.quantity
                existing_item.save()
                existing_item.refresh_from_db()
                serializer = CartItemSerializer(existing_item, context={"request": request})
                return Response(
                    {"message": "Item Updated successfully", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            serializer = CartItemSerializer(data=data, context={"request": request})
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

            serializer = CartItemSerializer(cart_item, data=request.data, partial=True, context={"request": request})
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
        try:
            """Delete an item from the cart."""
            # Retrieve and delete the cart item
            cart_item = get_object_or_404(
                CartItem, id=cart_item_id, cart__user=request.user
            )
            if cart_item:
                cart_item.delete()
                return Response(
                    {"message": "Item removed from cart successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Cart item doeys not exist."},
                    status=status.HTTP_404_NOT_FOUND,
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
            


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = Order.objects.filter(user=request.user)
            serializer = OrderSerializer(orders, many=True, context={"request": request})
            return Response(
                {"message": "Orders fetched successfully.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"Error occurred while fetching orders {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request):
        address_id = request.data.get("address_id")
        if not address_id:
            return Response(
                {
                    "message": "Address ID not provided.",
                    "data": ["address_id is required"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            address = CustomerAddress.objects.get(id=address_id)
        except CustomerAddress.DoesNotExist:
            return Response(
                {"message": "Address not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_cart, created = Cart.objects.get_or_create(user=request.user)
        if user_cart.items.count() == 0:
            return Response(
                {"message": "Cart is empty, add items before checkout."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        total_price = user_cart.calculate_original_price()
        final_price = user_cart.calculate_discounted_price()
        discount_applied = total_price - final_price

        # Razorpay client initialization
        client = razorpay.Client(
            auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET)
        )

        try:
            with transaction.atomic():
                # Create a local order
                order = Order.objects.create(
                    user=request.user,
                    total_price=total_price,
                    status="PENDING",
                    delivery_address=address,
                    final_price=final_price,
                    discount_applied=discount_applied,
                )

                # Add items to the order
                for item in user_cart.items.all():
                    if not item.product.in_stock():
                        raise ValueError(
                            "Some products are out of stock, please update your cart."
                        )
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.price,
                    )
                    order_item.save()
                    item.product.stock -= item.quantity
                    item.product.save()

                order.save()

                # Create a Razorpay Order
                razorpay_order = client.order.create(
                    {
                        "amount": int(final_price * 100),  # Amount in paise
                        "currency": "INR",
                        "receipt": f"order_rcptid_{order.id}",
                        "payment_capture": "1",
                    }
                )

                # Attach Razorpay Order ID to the local order
                order.razorpay_order_id = razorpay_order["id"]
                order.save()

            return Response(
                {
                    "message": "Order created successfully.",
                    "order_id": order.id,
                    "razorpay_order_id": razorpay_order["id"],
                    "amount": final_price,
                    "currency": "INR",
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {"message": "Some products are out of stock, please update your cart."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = VerifyPaymentSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                data = serializer.data
                print(data, "data from verify payment")
                razorpay_order_id = data["razorpay_order_id"]
                razorpay_payment_id = data["razorpay_payment_id"]
                razorpay_signature = data["razorpay_signature"]
                client = razorpay.Client(
                    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET)
                )
                client.utility.verify_payment_signature(
                    {
                        "razorpay_order_id": razorpay_order_id,
                        "razorpay_payment_id": razorpay_payment_id,
                        "razorpay_signature": razorpay_signature,
                    }
                )

                # If verification is successful, update order status
                order = Order.objects.filter(razorpay_order_id=razorpay_order_id, razorpay_payment_id=razorpay_payment_id).first()
                serializer = OrderSerializer(order, context={"request": request})
            else:
                return Response({"success": False, "message": serializer.errors})

            return Response(
                {"success": True, "message": "Payment verified successfully.","data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"success": False, "message": "Invalid payment signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Order.DoesNotExist:
            return Response(
                {"success": False, "message": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


@csrf_exempt
def razorpay_webhook( request):
    if request.method == "POST":
        try:
            received_signature = request.headers.get("X-Razorpay-Signature")
            payload = request.body.decode("utf-8")
            print(payload, "payload")
            client = razorpay.Client(
                auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET)
            )
            client.utility.verify_webhook_signature(
                payload, received_signature, "hello@123"
            )

            data = json.loads(payload)
            if data.get('event') ==  'payment.captured':
                payment_id = data["payload"]["payment"]["entity"]["id"]
                razorpay_order_id = data["payload"]["payment"]["entity"]["order_id"]
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.razorpay_payment_id = payment_id
                user = order.user
                order.save()
                user_cart, created = Cart.objects.get_or_create(user=user)
                if user_cart.coupon:
                    CouponUsage.objects.create(user=request.user, coupon=user_cart.coupon)
                user_cart.delete()
            elif data.get('event') == 'payment.failed':
                payment_id = data["payload"]["payment"]["entity"]["id"]
                razorpay_order_id = data["payload"]["payment"]["entity"]["order_id"]
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.razorpay_payment_id = payment_id
                order.status = "FAILED"
                order.save()
                user_cart, created = Cart.objects.get_or_create(user=request.user)
                # restock the stock if payment failed
                for item in user_cart.items.all():
                    item.product.stock += item.quantity
                    item.product.save()
                user_cart.delete()
            return JsonResponse({"message": "Webhook received successfully."}, status=200)
    
        except Exception as e:
            print(str(e), "error")
            return JsonResponse({"message": str(e)}, status=200)