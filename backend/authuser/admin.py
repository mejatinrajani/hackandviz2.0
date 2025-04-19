from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PhoneOTP

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'name', 'email', 'phone_number', 'is_active', 'is_staff', 'is_phone_verified')
    list_filter = ('is_active', 'is_staff', 'is_phone_verified')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_phone_verified')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'name', 'email', 'phone_number', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

# Phone OTP Admin
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'is_verified', 'created_at', 'is_expired')
    search_fields = ('user__username', 'user__email', 'otp')
    list_filter = ('is_verified',)
    ordering = ('-created_at',)
    
    # Optionally, you can add custom actions or fields to check OTP expiration, etc.
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True  # Display as a boolean icon in the admin

# Register models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PhoneOTP, PhoneOTPAdmin)
