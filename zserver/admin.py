from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from zserver.models import (
    Message,
    Session,
    SignUpOTP,
    UnverifiedUser,
    VerifyUserOTP,
)

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    list_display = ['email', 'contact', 'is_active', 'email_verified', 'is_staff', 'created_at']
    list_filter = ['is_active', 'email_verified', 'is_staff', 'is_superuser']
    search_fields = ['email', 'contact']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('contact',)}),
        ('Permissions', {'fields': ('is_active', 'email_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'contact', 'password1', 'password2', 'is_active', 'email_verified'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(SignUpOTP)
admin.site.register(Session)
admin.site.register(VerifyUserOTP)
admin.site.register(UnverifiedUser)
admin.site.register(Message)
