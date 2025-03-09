from django.contrib.admin import register
from django.contrib import admin
from .models import User, CustomerAddress
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm

@register(User)
class UserAdmin(ModelAdmin, ImportExportModelAdmin):
    imort_form_class = ImportForm
    export_form_class = ExportForm
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("email", "full_name", "is_wholesale_customer")
    search_fields = ("email", "full_name")
    list_filter = ("is_wholesale_customer", 'gender', 'email', 'is_active', 'is_staff', 'is_superuser')
    ordering = ("full_name")

@register(CustomerAddress)
class CustomerAddressAdmin(ModelAdmin):
    list_display = ('user', 'address_line_1', 'address_type', 'address_line_2', 'city', 'state', 'country', 'pincode')
    search_fields = ("user__email", "user__full_name", "address_line_1", "address_line_2", "city", "state", "country", "pincode")
    list_filter = ("address_type")