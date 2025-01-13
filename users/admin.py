from django.contrib import admin
from .models import User, CustomerAddress


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "is_wholesale_customer")
    search_fields = (
        "email",
        "full_name",
    )
    list_filter = ("is_wholesale_customer",)
    ordering = ("full_name",)


admin.site.register(User, UserAdmin)
admin.site.register(CustomerAddress)
