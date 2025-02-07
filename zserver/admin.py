from django.contrib import admin

from .models import Session, SignUpOTP, UserProfile

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(SignUpOTP)
admin.site.register(Session)
