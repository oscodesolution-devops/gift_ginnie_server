from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomerAddress
from .serializers import (
    UserSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    UserProfileSerializer,
    CustomerAddressSerializer,
)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from . import utils
from django.conf import settings

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


### [ TESTING ONLY ] ###
def get_test_tokens_for_current_user():
    refresh = RefreshToken.for_user(User.objects.first())
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class DummyTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(get_test_tokens_for_current_user(), status=status.HTTP_200_OK)


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.data["phone_number"]
            country_code = serializer.data["country_code"]
            message_central_customer_id = settings.MESSAGE_CENTRAL_CUSTOMER_ID
            message_central_password_key = settings.MESSAGE_CENTRAL_PASSWORD_KEY
            res = utils.send_otp(
                country_code,
                phone_number,
                message_central_customer_id,
                message_central_password_key,
            )
            if res != False:
                return Response(
                    {
                        "message": "OTP sent successfully",
                        "data": {
                            "verification_id": res["verificationId"],
                            "authToken": res["authToken"],
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            elif res["status"] == 506:
                return Response(
                    {
                        "message": "OTP already sent",
                        "verification_id": res["verificationId"],
                    },
                    status=status.HTTP_506_VARIANT_ALSO_NEGOTIATES,
                )
            else:
                return Response(
                    {"message": "OTP not sent"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.data["phone_number"]
            country_code = serializer.data["country_code"]
            otp = serializer.data["otp"]
            verification_id = serializer.data["verification_id"]
            token = serializer.data["token"]
            res = utils.verify_otp(
                verification_id,
                otp,
                token,
            )
            if res == True:
                try:
                    user = User.objects.filter(
                        phone_number=phone_number, country_code=country_code
                    ).first()
                    if not user:
                        user = User.objects.create_user(
                            phone_number=phone_number, country_code=country_code
                        )
                        return Response(
                            {
                                "message": "OTP verified successfully",
                                "data": get_tokens_for_user(user),
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response(
                            {
                                "message": "OTP verified successfully",
                                "data": get_tokens_for_user(user),
                            },
                            status=status.HTTP_200_OK,
                        )
                except Exception as e:
                    return Response(
                        {"message": e},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"message": "OTP not verified, Something went wrong"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_queryset(self):
        # Define a queryset for the logged-in user
        return User.objects.filter(pk=self.request.user.pk)

    def get_object(self):
        # Ensure it retrieves the logged-in user
        return self.request.user


    def update(self, request, *args, **kwargs):
        # Retrieve the user object
        try:
            partial = kwargs.pop("partial", False)  
            instance = self.get_object()
            if not request.data:
                return Response(
                    {
                        "message":"No data provided"
                    }
                )
            # Serialize and validate the incoming data
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                self.perform_update(serializer)
                return Response(
                    {
                        "message": "Profile updated successfully",
                        "data": serializer.data,  # Return updated user data
                    },
                    status=status.HTTP_200_OK,
                )
          
            else:
                return Response(
                    {
                        "message": "Profile update failed",
                        "data": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": "Profile update failed",
                    "data": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(
            {
                "message": "Profile fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AddressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomerAddressSerializer(user.addresses, many=True)
        return Response(
            {
                "message": "Addresses fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        user = request.user
        serializer = CustomerAddressSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(
                    {
                        "message": "Address added successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "message": "Address not added.",
                        "data": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": "Address not added.",
                    "data": e,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request, *args, **kwargs):
        user = request.user
        address_id = request.data.get("id")
        try:
            address = CustomerAddress.objects.get(id=address_id, user=user)
        except CustomerAddress.DoesNotExist:
            return Response(
                {
                    "message": "Address not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CustomerAddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Address updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "message": "Address not updated.",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        address_id:int = request.data.get("id")
        if not address_id:
            return Response(
                {"message": "Address ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            address = CustomerAddress.objects.get(id=address_id, user=user)
        except CustomerAddress.DoesNotExist:
            return Response(
                {
                    "message": "Address not found.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        address.delete()
        return Response(
            {"message": "Address deleted successfully.", "data": None},
            status=status.HTTP_204_NO_CONTENT,
        )
