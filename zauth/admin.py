from django.contrib import admin

from zauth.models import SignUpOTP, VerifyUserOTP

admin.site.register(SignUpOTP)
admin.site.register(VerifyUserOTP)
