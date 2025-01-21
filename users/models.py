from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from cloudinary.models import CloudinaryField


class UserManager(BaseUserManager):
    def create_user(self, phone_number=None, email=None, password=None, **extra_fields):
        """
        Create and return a user with a phone number or email.
        """
        if not phone_number and not email:
            raise ValueError("Either phone number or email must be set")

        if email:
            email = self.normalize_email(email)
            extra_fields.setdefault("is_staff", False)
            extra_fields.setdefault("is_superuser", False)

        user = self.model(phone_number=phone_number, email=email, **extra_fields)

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            email=email, phone_number=None, password=password, **extra_fields
        )


class CustomerAddress(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="addresses")
    address_line_1 = models.CharField(
        max_length=100,
    )
    address_type = models.CharField(
        max_length=10,
        choices=(
            ("H", "Home"),
            ("B", "Work"),
            ("O", "Other"),
        ),
    )
    address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)

    class Meta:
        verbose_name = "Customer Address"
        verbose_name_plural = "Customer Addresses"

    def __str__(self):
        return self.address_line_1 or "Unnamed Address"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
    country_code = models.CharField(max_length=5, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_image = CloudinaryField("profile_image", blank=True, null=True)
    is_wholesale_customer = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=1,
        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
        default="M",
    )
    USERNAME_FIELD = "email"

    # REQUIRED_FIELDS = ["phone_number"]
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    objects = UserManager()

    def __str__(self):
        return self.email or self.phone_number or "Unnamed User"
