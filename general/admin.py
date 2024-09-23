from django.contrib import admin
from .models import *
# Register your models here.
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp_code', 'created_at', 'attempts', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('phone_number', 'otp_code')
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        # Disable the add permission, as OTPs should only be created through the application
        return False

    def has_delete_permission(self, request, obj=None):
        # Optionally, allow deletion of old OTPs
        return True

# Register the OTP model with the admin site
admin.site.register(OTP, OTPAdmin)
