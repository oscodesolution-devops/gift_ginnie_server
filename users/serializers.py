from rest_framework import serializers
import cloudinary
import cloudinary.uploader
from giftginnie.global_serializers import CloudinaryImage
from .models import User, CustomerAddress


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10, required=True)
    country_code = serializers.CharField(max_length=10, required=True)

    class Meta:
        fields = ["phone_number", "country_code"]


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10, required=True)
    country_code = serializers.CharField(max_length=10, required=True)
    otp = serializers.CharField(max_length=6, required=True)
    token = serializers.CharField(max_length=1000, required=True)
    verification_id = serializers.CharField(max_length=10, required=True)

    class Meta:
        fields = ["phone_number", "country_code", "otp", "verification_id"]


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            "id",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "country",
            "pincode",
            "address_type",
        ]
        read_only_fields = ["id"]

    def validate_pincode(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Pincode must be a number")
        if len(value) != 6:
            raise serializers.ValidationError("Pincode must be 6 digits")
        return value

    def create(self, validated_data):
        return CustomerAddress.objects.create(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    addresses = CustomerAddressSerializer(many=True, read_only=False)
    profile_image = CloudinaryImage(read_only=True)
    image = serializers.ImageField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "phone_number",
            "country_code",
            "is_active",
            "profile_image",
            "is_wholesale_customer",
            "gender",
            "date_joined",
            "addresses",
            "image",
            # "image_url",
        ]
        read_only_fields = ["id", "date_joined", "profile_image"]

    def update(self, instance, validated_data):
        if "image" in validated_data:
            if instance.profile_image:
                res = cloudinary.uploader.destroy(
                    instance.profile_image.public_id, invalidate=True
                )
                print("profile image removed", res)
            validated_data["profile_image"] = validated_data.pop("image")
        return super().update(instance, validated_data)
